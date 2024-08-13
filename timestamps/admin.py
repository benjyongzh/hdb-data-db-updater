from django.contrib import admin
from timestamps.models import TablesLastUpdated
from api.serializers import TablesLastUpdatedSerializer

# Register your models here.
@admin.register(TablesLastUpdated)
class TablesLastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['table', 'last_updated']

def update_table_last_updated(table_name:str):
    last_updated = TablesLastUpdated.objects.update_or_create(table=table_name)
    serializer = TablesLastUpdatedSerializer(last_updated)
    return serializer.data
    
def get_table_last_updated(table_name:str):
    last_updated = TablesLastUpdated.objects.get(table=table_name)
    serializer = TablesLastUpdatedSerializer(last_updated)
    return serializer.data