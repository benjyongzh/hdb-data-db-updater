from django.contrib import admin
from .models import MrtStation, Line
from django.shortcuts import render
from django.urls import path
from common.forms import FileUploadForm, process_file_upload
from .util.parse_geojson import import_new_geojson_features_into_table, merge_polygons_with_intersection_logic, add_line_relationship
from common.util.utils import update_timestamps_table_lastupdated, get_table_lastupdated_datetime
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from io import BytesIO
from mrtstations.static_data import STATIONS

# Register your models here.
@admin.register(Line)
class BuildingGeometryPolygonAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'color']

@admin.register(MrtStation)
class BuildingGeometryPolygonAdmin(admin.ModelAdmin):
    list_display = ['name', 'rail_type']
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
                success_redirect_url="/api/mrt-stations/"
            )
        else:
            form = FileUploadForm()
            last_updated:str = get_table_lastupdated_datetime("mrtstations_mrtstation")
            form_context = {
                'form':form,
                'form_title': "Upload MRT Stations polygons .geojson file.",
                'table_last_updated': last_updated
            }
            
            # TODO if any, get task object in task table. with task_id. description of task
            return render(request, "admin/import_file.html", context=form_context)
        
@shared_task(bind=True)
def upload_geojson_impl(self, geojson_file):
    progress_recorder = ProgressRecorder(self)

    total_big_steps:int = 4

    with BytesIO(geojson_file) as file:
        geojson_features = import_new_geojson_features_into_table(
            MrtStation,
            file,
            progress_record={
                'progress_recorder': progress_recorder,
                'total_big_steps': total_big_steps
            })

    merge_polygons_with_intersection_logic(MrtStation,progress_record={
                'progress_recorder': progress_recorder,
                'total_big_steps': total_big_steps
            })

    progress_recorder.set_progress(1, 2, description=f"Step {total_big_steps} out of {total_big_steps}: Updating timestamp of last update of mrtstation table")
    
    add_line_relationship(MrtStation, Line, STATIONS, progress_record={
                'progress_recorder': progress_recorder,
                'total_big_steps': total_big_steps
            })
        
    # update table timestamp    
    # return {'table_last_updated': update_timestamps_table_lastupdated("postalcodes_buildinggeometrypolygon")}
    update_timestamps_table_lastupdated("mrtstations_mrtstation")

    progress_recorder.set_progress(2, 2, description="Finishing up")

    return "Geojson database update completed!"