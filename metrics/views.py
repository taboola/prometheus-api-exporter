from django.http import HttpResponse
from prometheus_client import CONTENT_TYPE_LATEST

from api_exporter.prometheus import REGISTRY, generate_latest


def metrics(request):
    endpoint = request.GET.get('target', None)
    if endpoint:
        data = generate_latest(REGISTRY, **{"endpoint": endpoint})
        return HttpResponse(
            data,
            content_type=CONTENT_TYPE_LATEST
        )
    else:
        return HttpResponse("No target specified")
