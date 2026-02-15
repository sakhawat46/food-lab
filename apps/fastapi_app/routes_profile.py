from fastapi import APIRouter, Depends, HTTPException, Body
from django.db import transaction

from apps.fastapi_app.auth import get_current_user
from apps.authentication.serializers import SellerProfileSerializer, CustomerProfileSerializer

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/")
def get_profile(current_user=Depends(get_current_user)):
    user = current_user

    if user.user_type == "seller":
        if not hasattr(user, "seller_profile"):
            raise HTTPException(status_code=404, detail="Seller profile not found")
        serializer = SellerProfileSerializer(user.seller_profile)
    else:
        if not hasattr(user, "customer_profile"):
            raise HTTPException(status_code=404, detail="Customer profile not found")
        serializer = CustomerProfileSerializer(user.customer_profile)

    return {"message": "Profile retrieved successfully", "data": serializer.data}


@router.put("/")
def update_profile(
    payload: dict = Body(...),  # body এখানে ধরছি (async লাগে না)
    current_user=Depends(get_current_user)
):
    user = current_user

    with transaction.atomic():
        if user.user_type == "seller":
            if not hasattr(user, "seller_profile"):
                raise HTTPException(status_code=404, detail="Seller profile not found")

            serializer = SellerProfileSerializer(
                user.seller_profile, data=payload, partial=True
            )

        else:
            if not hasattr(user, "customer_profile"):
                raise HTTPException(status_code=404, detail="Customer profile not found")

            serializer = CustomerProfileSerializer(
                user.customer_profile, data=payload, partial=True
            )

        if serializer.is_valid():
            serializer.save()
            return {"message": "Profile updated successfully", "data": serializer.data}

        raise HTTPException(status_code=400, detail=serializer.errors)