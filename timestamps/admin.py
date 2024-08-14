from django.contrib import admin
from timestamps.models import TablesLastUpdated
from api.serializers import TablesLastUpdatedSerializer
from datetime import datetime

# Register your models here.
@admin.register(TablesLastUpdated)
class TablesLastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['table', 'last_updated']

def update_table_last_updated(table_name:str):
    last_updated = TablesLastUpdated.objects.update_or_create(table=table_name)
    serializer = TablesLastUpdatedSerializer(last_updated)
    print(serializer.data)
    date = datetime(serializer.data)
    return date.strftime('%a %d %b %Y, %I:%M%p')
    
def get_table_last_updated(table_name:str):
    last_updated = TablesLastUpdated.objects.get(table=table_name)
    serializer = TablesLastUpdatedSerializer(last_updated)
    raw_date = serializer.data['last_updated'].split(".")[0]
    date = datetime.strptime(raw_date,'%Y-%m-%dT%H:%M:%S')
    return date.strftime('%a %d %b %Y, %I:%M%p')