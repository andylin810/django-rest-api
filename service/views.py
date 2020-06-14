from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from .serializers import AccountSerializer, RegistrationSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Account

# Create your views here.

class AccountDetail(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get_account(self,name):
        try:
            return Account.objects.get(username=name)
        except Account.DoesNotExist:
            raise Http404

    def get(self,request,name,format=None):
        user = self.get_account(name)
        if name != request.user.username:
            return Response("not allowed to view other user's account")
        serializer = AccountSerializer(user)
        return Response(serializer.data)
 
    def put(self, request, name, format=None):
        user = self.get_account(name)
        payee_name = ""
        response_data = {}
        try:
            payee_name = request.data.get('payee')
        except:
            response_data['error'] = "Invalid Payee"
            return Response(response_data)
        payee = self.get_account(payee_name)
        try:
            amount = request.data.get('balance')
            paid = user.pay_bill(amount)
            if paid is not None:
                payee.receive_money(amount)
                response_data['success'] = "payment success"
            else:
                response_data['error'] = "Insufficient fund"
            return Response(response_data)
        except:
            response_data['error'] = "unknown error"
            return Response(response_data)

class RegisterView(APIView):
    def post(self,request):
        serializer = RegistrationSerializer(data=request.data)
        response_data = {}
        if serializer.is_valid():
            account = serializer.save()
            response_data['reponse'] = "Registration Success"
            response_data['username'] = account.username
            response_data['email'] = account.email
            response_data['corperation'] = "yes" if account.corperation else "no"
        else:
            response_data = serializer.errors
        return Response(response_data)

