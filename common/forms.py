from django.forms import Form, FileField, FileInput
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from common.util.utils import update_timestamps_table_lastupdated, get_table_lastupdated_datetime


class FileUploadForm(Form):
    input_file = FileField(widget=FileInput(attrs={'class': 'form-control mb-4'}))

def process_file_upload(request, request_file_key:str, file_ext:str, success_try_func:callable, success_redirect_url:str):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid() and request.FILES[request_file_key]:
        uploaded_file = request.FILES[request_file_key]
        if not uploaded_file.name.endswith(file_ext):
            return JsonResponse({'error':f"File is not {file_ext} format."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            # start async celery task here and return response after starting task
            success_try_func.delay(uploaded_file)
            # data = update_timestamps_table_lastupdated("postalcodes_buildinggeometrypolygon")
            # resp = {"redirect_url": success_redirect_url, "table_last_updated": data}
            resp = {"redirect_url": success_redirect_url}
            return JsonResponse(resp, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error':f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error':'Form is invalid.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)