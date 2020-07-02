from rest_framework import serializers
from .models import Account, Bill
from django.db.models import Q

class BillSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField()
    payer = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ['billID','amount', 'description','receiver','payer','paid','date']

    def get_receiver(self,obj):
        return obj.receiver.username

    def get_payer(self,obj):
        return obj.payer.username

class AccountSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['username','email','company_name', 'phone_number', 'address', 'postal_code',
        'industry', 'balance','bill']
    
    def get_bill(self,obj):

        bills = Bill.objects.filter(Q(receiver__username = obj.username) | Q(payer__username = obj.username))
        return BillSerializer(bills,many=True).data


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type' : 'password'}, write_only=True)
    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'password2', 'corporation',
        'address','postal_code', 'phone_number', 'company_name', 'industry']
        extra_kwargs = {
            'password' : {'write_only' : True}
        }


    def save(self):
        account = Account(
            email=self.validated_data['email'],
            username = self.validated_data['username'],
            address = self.validated_data['address'],
            postal_code = self.validated_data['postal_code'],
            phone_number = self.validated_data['phone_number']
            )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if self.validated_data.get('corporation') is None:
            raise serializers.ValidationError({'corporation' : 'no corporation field'})
        if password != password2 :
            raise serializers.ValidationError({'password' : 'passwords dont match'})
        account.corporation = self.validated_data['corporation']
        if account.corporation:
            if self.validated_data.get('company_name') is None:
                raise serializers.ValidationError({'company_name' : 'no company name, company needs to have a name'})
            elif self.validated_data.get('industry') is None:
                raise serializers.ValidationError({'industry' : 'no industry, please indicate your industry'})
            else:
                account.company_name = self.validated_data['company_name']
                account.industry = self.validated_data['industry']
        account.set_password(password)
        account.save()
        return account


class PostBillSerializer(serializers.ModelSerializer):

    name = serializers.CharField()
    class Meta:
        model = Bill
        fields = ['billID', 'amount', 'name']

    def save(self):
        id = self.validated_data['billID']
        try:
            name = self.validated_data['name']
            user = Account.objects.get(username=name)
            bill,created = Bill.objects.get_or_create(
                billID=id,
                amount = self.validated_data['amount'],
                receiver = user,
                payer = user)
            if created:
                bill.save()
                return bill
            else:
                raise serializers.ValidationError({'billID' : 'Bill ID exists'})
        except Account.DoesNotExist:
            raise serializers.ValidationError({'account' : 'Account does not exist'})
