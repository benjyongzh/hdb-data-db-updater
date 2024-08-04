from django.contrib import admin
from resaletransactions.models import ResaleTransaction

class ResaleTransactionAdmin(admin.ModelAdmin):
    list_display = ['month', 'town', 'block', 'street_name', 'resale_price']

# Register your models here.
admin.site.register(ResaleTransaction, ResaleTransactionAdmin)