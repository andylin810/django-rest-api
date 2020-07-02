from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from .serializers import AccountSerializer, RegistrationSerializer, PostBillSerializer, BillSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Account, Bill

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
            return Response("not allowed to view other user's account", status=status.HTTP_400_BAD_REQUEST)
        serializer = AccountSerializer(user)
        return Response(serializer.data)
 
    def put(self, request, name, format=None):
        # get user account
        user = self.get_account(name)
        payee_name = ""
        response_data = {}
        bill = None

        # getting payee information if error return error message in Json reponse
        try:
            payee_name = request.data.get('payee')
        except:
            response_data['error'] = "Invalid Payee"
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        payee = Account.objects.get(username=payee_name)

        # getting bill information
        try:
            amount = request.data.get('balance')
            bill_id = request.data.get('billID')

            # if bill_id is received from json body
            if bill_id:
                # search for bill in database
                try:
                    bill = Bill.objects.get(billID=bill_id)
                    # validating bill if bill exists
                    if not bill.validate_bill(payee,amount,bill.paid):
                        response_data['bill_error'] = "Wrong bill"
                        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                # If bill doesn't exist create it
                except Bill.DoesNotExist:
                        bill = Bill(billID=bill_id,payer=user,receiver=payee,amount=amount,description=request.data.get('description'),paid=True)
                        bill.save()
            # if bill_id not indicated, create a new bill
            else:
                bill = Bill(user=user,company=payee,amount=amount,description=request.data.get('description'),paid=True) 

            paid = user.pay_bill(amount)

            # payment validated and recipient receives payment and bill gets saved
            if paid is not None:
                payee.receive_money(amount)
                bill.description = request.data.get('description')
                bill.paid = True
                bill.save()
                response_data['success'] = "payment success"
            else:
                response_data['error'] = "Insufficient fund"
            serializer = BillSerializer(bill)
            return Response(serializer.data)
        except:
            response_data['error'] = "unknown error"
            return Response(response_data,status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    def post(self,request):
        serializer = RegistrationSerializer(data=request.data)
        response_data = {}
        if serializer.is_valid():
            account = serializer.save()
            response_data['reponse'] = "Registration Success"
            response_data['username'] = account.username
            response_data['email'] = account.email
            if account.corporation:
                response_data['corporation'] = "yes"
                response_data['industry'] = account.industry
                response_data['company_name'] = account.company_name 
            else:
                response_data['corporation'] = "no"
            response_data['address'] = account.address
            response_data['postal_code'] = account.postal_code
            response_data['phone_number'] = account.phone_number
            return Response(response_data)
        else:
            response_data = serializer.errors
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class PostBillView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = PostBillSerializer(data=request.data)
        response_data = {}
        if serializer.is_valid():
            name = request.data.get("name")
            if name != request.user.username:
                return Response("You can only generate bill for you own account, please change name field to your username", status=status.HTTP_400_BAD_REQUEST)
            bill = serializer.save()
            response_data['reponse'] = "Post Bill Success"
            response_data['billID'] = bill.billID
            response_data['amount'] = bill.amount
            return Response(response_data)
        else:
            response_data = serializer.errors
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

