import requests
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from power_bi_embedded.base4 import PowerBIEmbedder


def power_bi_view(request):
    #### Azure #####
    application_id = "85265d74-7988-4136-b440-76f30e300103"
    application_secret = "WFz8Q~XxU2yLjY.4KozOQnL4CaMHfbbCFAJ0GbMw"
    tenant_id = "760dbe12-2907-4863-9716-576e540b56e4"
    ################

    ##### Power BI Service ######
    workspace_id = "d783142d-c793-4205-887d-b2509e04a614"
    report_id = "1ba9ea28-557e-41c8-867d-e32ac9faf188"
    dataset_id = "af4683b6-16ff-4f3c-ab4a-a6db7ed6f8ea"
    #############################

    ##### DB1 ######
    db1_parameters = {
        "server": "erp-staging.connectatelecom.net",
        "database": "dbemp00577_staging",
        "credentials": "voalle_db_lucasheinen:d6fI_iminoseDRaT",  # Codifique usuário:senha em Base64
    }
    ################

    ##### DB2 ######
    db2_parameters = {
        "server": "190.111.179.67:54504",
        "database": "dbemp00609_staging",
        "credentials": "voalle_db_lucasheinen:d6fI_iminoseDRaT",  # Codifique usuário:senha em Base64
    }
    ################
    

    powerbi = PowerBIEmbedder(
        application_id,
        workspace_id,
        report_id,
        application_secret,
        tenant_id,
        dataset_id,
        db_parameters=db1_parameters,
    )

    

    context = {
        "report_id": report_id,
        "embed_url": powerbi.embed_url,
        "embed_token": powerbi.embed_token,
    }
    return render(request, "power_bi_embedded/power_bi_embed.html", context)


def proxy_view(request):
    # Pass query parameters if needed
    params = request.GET.dict()

    TARGET_URL = "https://app.powerbi.com/view?r=eyJrIjoiOGFhZmE5YzYtMDkyNS00MjEzLWJlN2QtNDA4NTZiNTAwOWIwIiwidCI6IjEzNDVmNWQ0LWIzZWUtNDUzNC1iZDMxLWIyY2RhNWQyMDAwZCJ9"
    # Fetch content from the target URL
    response = requests.get(TARGET_URL, params=params)

    # Return the content to the client
    return HttpResponse(
        response.content,
        status=response.status_code,
        content_type=response.headers["Content-Type"],
    )


def power_bi_view_url(request):
    # Redireciona para a URL do Power BI
    return redirect(
        "https://app.powerbi.com/view?r=eyJrIjoiOGFhZmE5YzYtMDkyNS00MjEzLWJlN2QtNDA4NTZiNTAwOWIwIiwidCI6IjEzNDVmNWQ0LWIzZWUtNDUzNC1iZDMxLWIyY2RhNWQyMDAwZCJ9"
    )
