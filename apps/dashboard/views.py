from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractMonth
import calendar
from rest_framework import status

from apps.order.models import Order
from apps.authentication.models import User


class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code= status.HTTP_200_OK):
        return Response(
            {
            "success": True,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )
    def error_response(self, message="Your request rejected", data=None, status_code= status.HTTP_400_BAD_REQUEST):
        return Response(
            {
            "success": False,
            "message": message,
            "status": status_code,
            "data": data or {}
            },
            status=status_code )  


class DashboardSummaryView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now().date()
        week_ago = today - timedelta(days=7)
        prev_week = today - timedelta(days=14)

        total_orders = Order.objects.count()
        total_customers = User.objects.filter(user_type='customer').count()

        current_orders = Order.objects.filter(created_at__date__gte=week_ago)
        previous_orders = Order.objects.filter(created_at__date__range=(prev_week, week_ago))

        current_new_customers = User.objects.filter(date_joined__date__gte=week_ago, user_type='customer')
        previous_new_customers = User.objects.filter(date_joined__date__range=(prev_week, week_ago), user_type='customer')

        order_change = ((current_orders.count() - previous_orders.count()) / max(previous_orders.count(), 1)) * 100
        customer_change = ((current_new_customers.count() - previous_new_customers.count()) / max(previous_new_customers.count(), 1)) * 100

        data = {
            "total_orders": total_orders,
            "total_orders_change": round(order_change),
            "total_customers": total_customers,
            "total_customers_change": round(customer_change)
        }

        return self.success_response(
            message="Dashboard summary retrieved successfully.",
            data=data,
            status_code=status.HTTP_200_OK
        )



class RevenueChartView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        range_type = request.GET.get("range", "weekly")
        today = now().date()

        if range_type == "monthly":
            current_year = today.year

            queryset = (
                Order.objects.filter(created_at__year=current_year)
                .annotate(month=ExtractMonth("created_at"))
                .values("month")
                .annotate(total=Sum("grand_total"))
            )

            month_totals = {item["month"]: float(item["total"]) for item in queryset}

            data = []
            total_revenue = 0
            for month_number in range(1, 13):
                month_name = calendar.month_abbr[month_number]
                amount = month_totals.get(month_number, 0)
                total_revenue += amount
                data.append({
                    "month": month_name,
                    "amount": amount
                })

            return self.success_response(
                message="Monthly revenue chart generated.",
                data={
                    "range": "monthly",
                    "total_revenue": total_revenue,
                    "data": data
                },
                status_code=status.HTTP_200_OK
            )

        # ---- Weekly fallback ----
        start_date = today - timedelta(days=6)
        total_revenue = 0
        data = []

        for i in range(7):
            day = start_date + timedelta(days=i)
            total = Order.objects.filter(created_at__date=day).aggregate(
                revenue=Sum("grand_total")
            )["revenue"] or 0

            amount = float(total)
            total_revenue += amount
            data.append({
                "day": day.strftime("%a"),  # e.g. Mon, Tue
                "amount": amount
            })

        return self.success_response(
            message="Weekly revenue chart generated.",
            data={
                "range": "weekly",
                "total_revenue": total_revenue,
                "data": data
            },
            status_code=status.HTTP_200_OK
        )


class CustomerChartView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        range_type = request.GET.get("range", "weekly")
        today = now().date()

        if range_type == "monthly":
            current_year = today.year

            queryset = (
                User.objects.filter(date_joined__year=current_year, user_type='customer')
                .annotate(month=ExtractMonth("date_joined"))
                .values("month")
                .annotate(count=Count("id"))
            )

            month_counts = {item["month"]: item["count"] for item in queryset}

            data = []
            for month_number in range(1, 13):
                month_name = calendar.month_abbr[month_number]
                count = month_counts.get(month_number, 0)
                data.append({
                    "month": month_name,
                    "count": count
                })

            return self.success_response(
                message="Monthly customer chart generated.",
                data={
                    "range": "monthly",
                    "data": data
                },
                status_code=status.HTTP_200_OK
            )

        # ---- Weekly fallback ----
        start_date = today - timedelta(days=6)
        data = []

        for i in range(7):
            day = start_date + timedelta(days=i)
            count = User.objects.filter(
                date_joined__date=day,
                user_type='customer'
            ).count()
            data.append({
                "day": day.strftime("%a"),
                "count": count
            })

        return self.success_response(
            message="Weekly customer chart generated.",
            data={
                "range": "weekly",
                "data": data
            },
            status_code=status.HTTP_200_OK
        )