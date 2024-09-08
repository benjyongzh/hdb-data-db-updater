# views.py
from django.http import StreamingHttpResponse, Http404
from celery_progress.backend import Progress
from celery.result import AsyncResult
import json

def get_task_progress(request, task_id):
    """
    Custom view to handle Server-Sent Events (SSE) correctly for Celery task progress.
    """

    # Function to stream progress updates as an SSE
    def event_stream():
        # Fetch the task result using the provided task ID
        task_result = AsyncResult(task_id)
        # Check if the task exists and is recognized by Celery
        if task_result is None:
            raise Http404(f"No task found with id: {task_id}")

        # Create a Progress object to manage task state
        progress = Progress(task_result)
        # print("progress:", progress)

        # Continuously yield progress updates
        while not task_result.ready():  # Stream until the task is completed
            # progress_data = progress.to_dict()  # Get progress as a dictionary
            yield f"data: {json.dumps(progress.get_info())}\n\n"  # Send the data in SSE format

    # Return the response with content type 'text/event-stream'
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    return response
