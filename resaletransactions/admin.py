from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from resaletransactions.models import ResaleTransaction
from resaletransactions.util.csv_operations import update_table_with_csv
from common.forms import FileUploadForm, process_file_upload
from common.util.utils import update_timestamps_table_lastupdated

# Register your models here.
@admin.register(ResaleTransaction)
class ResaleTransactionAdmin(admin.ModelAdmin):
    list_display = ['month', 'town', 'block', 'street_name', 'resale_price']

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
            form_context = {
                'form':form,
                'form_title': "Upload resale transactions .csv file.",
            }
            return render(request, "admin/import_file.html", context=form_context)

def upload_csv_file_impl(input_file) -> None:
    update_table_with_csv("resaletransactions_resaletransaction", input_file)
        
    # update table timestamp
    update_timestamps_table_lastupdated("resaletransactions_resaletransaction")
