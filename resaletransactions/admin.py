from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from resaletransactions.models import ResaleTransaction
from resaletransactions.util.csv_operations import update_resaletransactions_table_with_csv,update_postalcodes_from_empty_resaletransactions_postalcodes
from common.forms import FileUploadForm, process_file_upload
from common.util.utils import update_timestamps_table_lastupdated, get_table_lastupdated_datetime, update_tableA_FK_match_with_tableB_PK_on_matching_columns
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from io import BytesIO

# Register your models here.
@admin.register(ResaleTransaction)
class ResaleTransactionAdmin(admin.ModelAdmin):
    list_display = ['unit', 'flat_type', 'town', 'month', 'resale_price']

    @admin.display(description="Unit")
    def unit(self, obj):
        return f"{obj.street_name} Blk {obj.block}, {obj.floor_area_sqm} sqm, {obj.storey_range} storey".upper()

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            # create table for tasks (id, application:str, description:str, status:str, last-updated:datetime)
            # create a task scheduler core application. with views and urls to activate certain tasks
            
            # create task object with id
            # make upload_csv_file_impl update task object

            return process_file_upload(
                request,
                request_file_key='input_file',
                file_ext='.csv',
                success_try_func=upload_csv_file_impl,
                success_redirect_url="/api/resale-transactions/"
            )
        else:
            form = FileUploadForm()
            last_updated:str = get_table_lastupdated_datetime("resaletransactions_resaletransaction")
            form_context = {
                'form':form,
                'form_title': "Upload resale transactions .csv file.",
                'table_last_updated': last_updated
            }
            return render(request, "admin/import_file.html", context=form_context)

@shared_task(bind=True)
def upload_csv_file_impl(self,input_file):
    progress_recorder = ProgressRecorder(self)

    progress_recorder.set_progress(1, 5, description="Adding new rows to database from csv file")

    with BytesIO(input_file) as file:
        update_resaletransactions_table_with_csv("resaletransactions_resaletransaction", file, "tmp_table")

    progress_recorder.set_progress(2, 5, description="Updating foreign keys of new rows using existing records")

    update_tableA_FK_match_with_tableB_PK_on_matching_columns(
        table_a_name="resaletransactions_resaletransaction",
        table_b_name="postalcodes_postalcodeaddress",
        a_foreignkey_column_name="postal_code_key_id",
        b_primary_key_column_name="id",
        table_a_to_table_b_columns={
            "block": "block",
            "street_name": "street_name"
        })
    
    progress_recorder.set_progress(3, 5, description="Checking and updating record of postal codes")
    
    rows_still_null = ResaleTransaction.objects.filter(postal_code_key_id__isnull=True)
    if len(rows_still_null) > 0:
        update_postalcodes_from_empty_resaletransactions_postalcodes(rows_still_null)

    progress_recorder.set_progress(4, 5, description="Updating timestamp of last update of resaletransaction table")
    
    # update table timestamp
    update_timestamps_table_lastupdated("resaletransactions_resaletransaction")
    
    progress_recorder.set_progress(5, 5, description="Finishing up")

    return "Resale Transactions database update completed!"
