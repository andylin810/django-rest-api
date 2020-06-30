from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, username, password, address, postal_code, phone_number):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a user name')
        if not address:
            raise ValueError('Users must have an address')
        if not postal_code:
            raise ValueError('Users must have a postal code')
        if not phone_number:
            raise ValueError('Users must have a phone number')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            address = address,
            phone_number = phone_number,
            postal_code = postal_code
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, address, postal_code, phone_number):
        user = self.create_user(
            email,
            username,
            password,
            address,
            postal_code,
            phone_number
        )

        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):  
    email = models.EmailField(
        max_length=50,
        unique=True,
    )
    username = models.CharField(max_length=30, unique=True)
    balance = models.FloatField(default=0)
    corporation = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)

    industry = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=30)
    phone_number = models.IntegerField()
    company_name = models.CharField(max_length=30, blank=True, null=True)




    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'address', 'postal_code', 'phone_number']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def pay_bill(self,amount):
        self.balance -= amount
        if self.balance < 0:
            return None
        else :
            self.save()
            return self.balance
    
    def receive_money(self,amount):
        self.balance += amount
        self.save()

class Bill(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,related_name="user_bill")
    company = models.ForeignKey(Account,on_delete=models.CASCADE)
    amount = models.FloatField()
    description = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        if self.company.corporation:
            super(Bill,self).save(*args,**kwargs)
        else:
            raise Exception("only company can create bills")

    def validate_bill(self,user,company,amount,paid):
            return self.user == user and self.company == company and self.amount == amount and not paid