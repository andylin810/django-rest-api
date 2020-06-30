from rest_framework import serializers
from .models import Account, Bill

class BillSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ['id','amount', 'description','company','user','paid']

    def get_company(self,obj):
        return obj.company.username

    def get_user(self,obj):
        return obj.user.username

class AccountSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['username','email','balance','bill']
    
    def get_bill(self,obj):
        if obj.corporation:
            return BillSerializer(obj.bill_set,many=True).data
        else:
            return BillSerializer(obj.user_bill,many=True).data


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
                account.company_name = self.validated_data['corporation']
                account.industry = self.validated_data['industry']
        account.set_password(password)
        account.save()
        return account