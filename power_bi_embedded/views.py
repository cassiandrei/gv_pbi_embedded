import requests
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect

from gv_pbi_embedded.base import PowerBIEmbedder


def power_bi_view(request):
    # Exemplo de uso:
    powerbi = PowerBIEmbedder(
        application_id="0e8c2906-5218-4c4b-8ff3-4c1165078879",
        workspace_id="8a9d43bd-baa4-4884-9361-03b664cf3551",
        report_id="b465f0ac-f047-4404-b18d-d32a15d98bf7",
        application_secret="gAG8Q~iHgtSshl6DeH3FCtm0m56qJniyVk55CaXN",
        tenant_id="1345f5d4-b3ee-4534-bd31-b2cda5d2000d"
    )
    iframe_html = powerbi.generate_iframe()
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
