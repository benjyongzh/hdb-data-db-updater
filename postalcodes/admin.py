from django.contrib import admin
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from django.shortcuts import render
from django.urls import path
from common.forms import FileUploadForm, process_file_upload
from postalcodes.util.parse_geojson import import_new_geojson_features_into_table

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
                'form_title': "Refresh and update the mapping table of postal codes and addresses",
                'table_name': "postalcodes_postalcodeaddress"
            }
            return render(request, "admin/update_mapping.html", context=form_context)

def update_postalcode_address_table_impl():
    # update building polygons table
    table_to_upload:str = "postalcodes_postalcodeaddress"
    import_new_geojson_features_into_table(BuildingGeometryPolygon, upload_file)
    return

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