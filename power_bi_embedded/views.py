import requests
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect


def power_bi_view(request):
    # Adicione o URL do relatório do Power BI
    power_bi_url = "https://app.powerbi.com/reportEmbed?reportId=SEU_REPORT_ID&groupId=SEU_GROUP_ID"

    context = {
        'power_bi_url': power_bi_url,
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
