from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Bill

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('username', 'email', 'balance', 'date_joined', 'corperation') 
    search_fields = ('email','username')
    readonly_fields = ['date_joined']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account,AccountAdmin)
admin.site.register(Bill)