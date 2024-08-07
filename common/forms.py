from django.forms import Form, FileField, FileInput
from django.http import JsonResponse, HttpResponse
from rest_framework import status


class FileUploadForm(Form):
    input_file = FileField(widget=FileInput(attrs={'class': 'form-control mb-4'}))

def process_file_upload(request, request_file_key:str, file_ext:str, success_try_func:callable, success_redirect_url:str):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid() and request.FILES[request_file_key]:
        geojson_file = request.FILES[request_file_key]
        if not geojson_file.name.endswith(file_ext):
            return HttpResponse(f"File is not {file_ext} format.", status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            success_try_func(geojson_file)
            data = {"redirect_url": success_redirect_url}
            return JsonResponse(data, status=status.HTTP_200_OK)
        except:
            return JsonResponse({'error':'Could not complete file upload.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'error':'Form is invalid.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)