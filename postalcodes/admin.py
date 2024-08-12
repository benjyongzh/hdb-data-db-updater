from django.contrib import admin
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from django.shortcuts import render
from django.urls import path
from common.forms import FileUploadForm, process_file_upload
from postalcodes.util.parse_geojson import import_new_geojson_features_into_table
from postalcodes.util.postal_codes import update_postalcode_address_table
from rest_framework import status
from django.http import JsonResponse
from common.util.utils import update_timestamps_table_lastupdated

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
            return update_postalcode_address_table_impl()
        else:
            form_context = {
                'form_title': "Update Postalcode-Address Relation Table",
                'form_subtitle': "Refresh and update the mapping table of postal codes and addresses.",
                'table_name': "postalcodes_postalcodeaddress",

            }
            return render(request, "admin/update_mapping.html", context=form_context)

def update_postalcode_address_table_impl():
    try:
        data = update_postalcode_address_table()
    except Exception as e:
        return JsonResponse({'error':f"Could not update postalcode-address table: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # update table timestamp
    update_timestamps_table_lastupdated("postalcodes_postalcodeaddress")

    resp = {"redirect_url": "/api/postal-codes/", "new_addresses": data}
    return JsonResponse(resp, status=status.HTTP_200_OK)

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
            form_context = {
                'form':form,
                'form_title': "Upload HDB building polygons .geojson file.",
            }
            return render(request, "admin/import_file.html", context=form_context)
        
def upload_geojson_impl(geojson_file) -> None:
    import_new_geojson_features_into_table(BuildingGeometryPolygon, geojson_file)
        
    # update table timestamp
    update_timestamps_table_lastupdated("postalcodes_buildinggeometrypolygon")