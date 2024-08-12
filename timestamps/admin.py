from django.contrib import admin
from timestamps.models import TablesLastUpdated

# Register your models here.
@admin.register(TablesLastUpdated)
class TablesLastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['table', 'last_updated']

def update_tables_last_updated(table_name:str):
    TablesLastUpdated.objects.update_or_create(table=table_name)