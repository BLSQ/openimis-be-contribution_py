# Register your models here.
from django.contrib import admin
# Register your models here.
from .models import PaymentServiceProvider, Premium

admin.site.register(PaymentServiceProvider)
admin.site.register(Premium)
