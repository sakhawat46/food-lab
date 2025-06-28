from django.urls import path
from .views import DashboardSummaryView, RevenueChartView, CustomerChartView

urlpatterns = [
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/revenue/', RevenueChartView.as_view(), name='dashboard-revenue'),
    path('dashboard/customers/', CustomerChartView.as_view(), name='dashboard-customers'),
]
