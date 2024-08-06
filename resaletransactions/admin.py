from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from resaletransactions.models import ResaleTransaction
from resaletransactions.util.csv_operations import update_table_with_csv
from forms import FileUploadForm

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
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid() and request.FILES['input_file']:
                csv_file = request.FILES['input_file']
                if not csv_file.name.endswith('.csv'):
                    return HttpResponse('File is not CSV.', status=status.HTTP_406_NOT_ACCEPTABLE)

                # update resale transactions table
                try:
                    update_table_with_csv("resaletransactions_resaletransaction", csv_file)
                    data = {"redirect_url": "/api/resale-transactions/"}
                    return JsonResponse(data, status=status.HTTP_200_OK)

                except:
                    return JsonResponse({'error':'Could not complete file upload.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({'error':'Form is invalid.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            form = FileUploadForm()
            form_context = {
                'form':form,
                'form_title': "Upload resale transactions .csv file.",
            }
            return render(request, "admin/import_file.html", context=form_context)

    