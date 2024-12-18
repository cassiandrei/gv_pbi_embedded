import requests
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect

from gv_pbi_embedded.base4 import (PowerBIEmbedder)


def power_bi_view(request):
    # Exemplo de uso:
    powerbi = PowerBIEmbedder(
        application_id="750de238-6035-48a4-ae47-01ca6e55e53b",
        workspace_id="8d1c951b-5b2c-4903-9364-16788c518ab8",
        report_id="40a0a66c-d422-4c91-82ab-3c5171e16fad",
        application_secret="aiv8Q~j3Fc6J3H~eWRBF8vzQrrISnaFOcPpc7dvn",
        tenant_id="1345f5d4-b3ee-4534-bd31-b2cda5d2000d"
    )
    iframe_html = powerbi.generate_embed_iframe(width="1200px", height="700px")
    context = {
        'iframe_html': iframe_html,
    }
    return render(request, 'power_bi_embedded/power_bi_embed.html', context)


def proxy_view(request):
    # Pass query parameters if needed
    params = request.GET.dict()

    TARGET_URL = 'https://app.powerbi.com/view?r=eyJrIjoiOGFhZmE5YzYtMDkyNS00MjEzLWJlN2QtNDA4NTZiNTAwOWIwIiwidCI6IjEzNDVmNWQ0LWIzZWUtNDUzNC1iZDMxLWIyY2RhNWQyMDAwZCJ9'
    # Fetch content from the target URL
    response = requests.get(TARGET_URL, params=params)

    # Return the content to the client
    return HttpResponse(response.content, status=response.status_code, content_type=response.headers['Content-Type'])

def power_bi_view_url(request):
    # Redireciona para a URL do Power BI
    return redirect(
        "https://app.powerbi.com/view?r=eyJrIjoiOGFhZmE5YzYtMDkyNS00MjEzLWJlN2QtNDA4NTZiNTAwOWIwIiwidCI6IjEzNDVmNWQ0LWIzZWUtNDUzNC1iZDMxLWIyY2RhNWQyMDAwZCJ9")
