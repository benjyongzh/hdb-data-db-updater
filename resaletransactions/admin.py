from django.contrib import admin
from django.urls import path
from django import forms
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseRedirect, HttpResponse
from resaletransactions.models import ResaleTransaction
from django.shortcuts import render
# from import_export.admin import ImportExportModelAdmin, ImportMixin
from resaletransactions.util.csv_operations import update_table_with_csv

# Register your models here.
@admin.register(ResaleTransaction)
# class ResaleTransactionAdmin(ImportMixin ,admin.ModelAdmin):
class ResaleTransactionAdmin(admin.ModelAdmin):
    list_display = ['month', 'town', 'block', 'street_name', 'resale_price']

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            if request.FILES['resale_csv_file']:
                csv_file = request.FILES['resale_csv_file']
                if not csv_file.name.endswith('.csv'):
                    # return Response({'error': 'File is not CSV.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    return HttpResponse('File is not CSV.', status=status.HTTP_406_NOT_ACCEPTABLE)

                # update resale transactions table
                try:
                    update_table_with_csv("resaletransactions_resaletransaction", csv_file)

                    # update postalcodes table

                    # response
                    data = {"redirect_url": "/api/resale-transactions/"}
                    # return Response(data, status=status.HTTP_200_OK)
                    return HttpResponse(data, status=status.HTTP_200_OK)

                except:
                    # return Response({'error': 'Server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    return HttpResponse('Server error.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return render(request, "admin/import_resale_transactions.html")

    