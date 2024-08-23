from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from resaletransactions.models import ResaleTransaction
from resaletransactions.util.csv_operations import update_resaletransactions_table_with_csv,update_resaletransactions_foreignkey_on_postalcodes
from common.forms import FileUploadForm, process_file_upload
from common.util.utils import update_timestamps_table_lastupdated, get_table_lastupdated_datetime

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

def upload_csv_file_impl(input_file):
    update_resaletransactions_table_with_csv("resaletransactions_resaletransaction", input_file, "postal_code_id_id")

    update_resaletransactions_foreignkey_on_postalcodes(related_col_id="id")
        
    # update table timestamp
    return {'table_last_updated': update_timestamps_table_lastupdated("resaletransactions_resaletransaction")}
