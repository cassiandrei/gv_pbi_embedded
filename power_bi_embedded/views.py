from django.shortcuts import render

from power_bi_embedded.base import PowerBIEmbedder


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

    ##### DBs ######
    db1_parameters = {
        "server": "erp-staging.connectatelecom.net",
        "database": "dbemp00577_staging",
        "credentials": "voalle_db_lucasheinen:d6fI_iminoseDRaT",
    }

    db2_parameters = {
        "server": "190.111.179.67:54504",
        "database": "dbemp00609_staging",
        "credentials": "voalle_db_lucasheinen:d6fI_iminoseDRaT",
    }

    db3_parameters = {
        "server": "erp-staging.speednettelecom.com.br",
        "database": "dbemp00594_staging",
        "credentials": "voalle_db_lucasheinen:d6fI_iminoseDRaT",
    }
    ################

    powerbi = PowerBIEmbedder(
        application_id,
        workspace_id,
        report_id,
        application_secret,
        tenant_id,
        dataset_id,
        db_parameters=db3_parameters,
    )

    context = {
        "report_id": report_id,
        "embed_url": powerbi.embed_url,
        "embed_token": powerbi.embed_token,
    }
    return render(request, "power_bi_embedded/power_bi_embed.html", context)
