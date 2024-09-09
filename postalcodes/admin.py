from django.contrib import admin
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from django.shortcuts import render
from django.urls import path
from common.forms import FileUploadForm, process_file_upload
from postalcodes.util.parse_geojson import import_new_geojson_features_into_table
from postalcodes.util.postal_codes import update_postalcode_address_table
from rest_framework import status
from django.http import JsonResponse
from common.util.utils import update_timestamps_table_lastupdated, get_table_lastupdated_datetime,update_tableA_FK_match_with_tableB_PK_on_matching_columns
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from io import BytesIO

# Register your models here.
@admin.register(PostalCodeAddress)
class PostalCodeAddressAdmin(admin.ModelAdmin):
    list_display = ['block', 'street_name', 'postal_code']

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('update-mapping/', self.update_postalcode_address_table),]
        return new_urls + urls

    def update_postalcode_address_table(self, request):
        if request.method == "POST":
            data = update_postalcode_address_table_impl()
            return JsonResponse(data, status=status.HTTP_200_OK)
        else:
            last_updated:str = get_table_lastupdated_datetime("postalcodes_postalcodeaddress")
            form_context = {
                'form_title': "Update Postalcode-Address Relation Table",
                'form_subtitle': "Refresh and update the mapping table of postal codes and addresses.",
                'table_name': "postalcodes_postalcodeaddress",
                'table_last_updated': last_updated

            }
            return render(request, "admin/update_mapping.html", context=form_context)

def update_postalcode_address_table_impl():
    try:
        data = update_postalcode_address_table()
    except Exception as e:
        return JsonResponse({'error':f"Could not update postalcode-address table: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # update table timestamp
    resp = {
        "redirect_url": "/api/postal-codes/",
        "new_addresses": data,
        'table_last_updated': update_timestamps_table_lastupdated("postalcodes_postalcodeaddress")
    }
    return resp

@admin.register(BuildingGeometryPolygon)
class BuildingGeometryPolygonAdmin(admin.ModelAdmin):
    list_display = ['block', 'postal_code', 'building_polygon']
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-geojson/', self.upload_geojson),]
        return new_urls + urls

    def upload_geojson(self, request):
        if request.method == "POST":
            return process_file_upload(
                request,
                request_file_key='input_file',
                file_ext='.geojson',
                success_try_func=upload_geojson_impl,
                success_redirect_url="/api/building-polygons/"
            )
        else:
            form = FileUploadForm()
            last_updated:str = get_table_lastupdated_datetime("postalcodes_buildinggeometrypolygon")
            form_context = {
                'form':form,
                'form_title': "Upload HDB building polygons .geojson file.",
                'table_last_updated': last_updated
            }
            return render(request, "admin/import_file.html", context=form_context)
        
@shared_task(bind=True)
def upload_geojson_impl(self, geojson_file):
    progress_recorder = ProgressRecorder(self)

    steps_remaining:int = 2

    with BytesIO(geojson_file) as file:
        geojson_features = import_new_geojson_features_into_table(BuildingGeometryPolygon, file, progress_recorder,steps_remaining)

    total_steps = steps_remaining + len(geojson_features)

    progress_recorder.set_progress(total_steps-1, total_steps, description="Updating Foreign Keys")

    update_tableA_FK_match_with_tableB_PK_on_matching_columns(
        table_a_name="postalcodes_buildinggeometrypolygon",
        table_b_name="postalcodes_postalcodeaddress",
        a_foreignkey_column_name="postal_code_key_id",
        b_primary_key_column_name="id",
        table_a_to_table_b_columns={
            "block": "block",
            "postal_code": "postal_code"
        }
    )

    progress_recorder.set_progress(total_steps, total_steps, description="Updating timestamp of last update of buildinggeometrypolygon table")
        
    # update table timestamp    
    # return {'table_last_updated': update_timestamps_table_lastupdated("postalcodes_buildinggeometrypolygon")}
    update_timestamps_table_lastupdated("postalcodes_buildinggeometrypolygon")

    return "Geojson database update completed!"