from django.contrib import admin
from timestamps.models import TablesLastUpdated
from api.serializers import TablesLastUpdatedSerializer
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# Register your models here.
@admin.register(TablesLastUpdated)
class TablesLastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['table', 'last_updated']

def update_table_last_updated(table_name:str):
    try:
        last_updated = TablesLastUpdated.objects.update(table=table_name)
    except ObjectDoesNotExist as e:
        last_updated = TablesLastUpdated.objects.create(table=table_name)
    finally:
        date_object = get_datetime_object_from_model_object(last_updated)
        return format_datetime_object_to_string(date_object)
    
def get_table_last_updated(table_name:str):
    try:
        last_updated = TablesLastUpdated.objects.get(table=table_name)
    except ObjectDoesNotExist as e:
        # should let function return None if really None
        last_updated = TablesLastUpdated.objects.create(table=table_name)
    finally:
        date_object = get_datetime_object_from_model_object(last_updated)
        return format_datetime_object_to_string(date_object)

def get_datetime_object_from_model_object(obj):
        serializer = TablesLastUpdatedSerializer(obj)
        raw_date = serializer.data['last_updated'].split(".")[0]
        return datetime.strptime(raw_date,'%Y-%m-%dT%H:%M:%S')
    
def format_datetime_object_to_string(datetime_object):
    # set timezone
    if settings.TIMEZONE_HOURS:
        date = datetime_object + timedelta(hours=settings.TIMEZONE_HOURS)
        if settings.TIMEZONE_HOURS > 0:
            timezone_str: str = f"GMT +{settings.TIMEZONE_HOURS}:00"
        else:
            timezone_str: str = f"GMT -{abs(settings.TIMEZONE_HOURS)}:00"
    else:
        timezone_str: str = "GMT"
            
    final_str: str = f"{date.strftime('%a %d %b %Y, %I:%M%p')}, {timezone_str}"
    return final_str