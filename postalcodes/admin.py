from django.contrib import admin
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import path
from rest_framework import status
from forms import FileUploadForm

# Register your models here.
@admin.register(PostalCodeAddress)
class PostalCodeAddressAdmin(admin.ModelAdmin):
    list_display = ['block', 'street_name', 'postal_code']

    
@admin.register(BuildingGeometryPolygon)
class BuildingGeometryPolygonAdmin(admin.ModelAdmin):
    list_display = ['block', 'postal_code', 'building_polygon']
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-geojson/', self.upload_geojson),]
        return new_urls + urls

    def upload_geojson(self, request):
        if request.method == "POST":
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid() and request.FILES['input_file']:
                geojson_file = request.FILES['input_file']
                if not geojson_file.name.endswith('.geojson'):
                    return HttpResponse('File is not GeoJSON.', status=status.HTTP_406_NOT_ACCEPTABLE)

                # update geojsons table
                try:
                    #! use function of going thru geojson to update table here
                    # update_table_with_csv("resaletransactions_resaletransaction", geojson_file)

                    data = {"redirect_url": "/api/building-polygons/"}
                    return JsonResponse(data, status=status.HTTP_200_OK)

                except:
                    return JsonResponse({'error':'Could not complete file upload.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({'error':'Form is invalid.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            form = FileUploadForm()
            form_context = {
                'form':form,
                'form_title': "Upload HDB building polygons .geojson file.",
            }
            return render(request, "admin/import_file.html", context=form_context)