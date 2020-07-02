from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register('accounts/<str:name>',views.account_detail)

urlpatterns = [
    path('account/detail/<str:name>/', views.AccountDetail.as_view()),
    path('account/register/', views.RegisterView.as_view()),
    path('account/bill/generate/', views.PostBillView.as_view()),
]


