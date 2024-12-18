import requests
import json

class PowerBIEmbedder:
    def __init__(self, application_id, workspace_id, report_id, application_secret, tenant_id):
        self.application_id = application_id
        self.workspace_id = workspace_id
        self.report_id = report_id
        self.application_secret = application_secret
        self.tenant_id = tenant_id
        self.dataset_id = '4bd9a7f8-b0e5-4baf-9dc6-62dd22fc1619'

    def get_access_token(self):
        # URL para obter o token
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        # Dados para a requisição do token
        data = {
            "grant_type": "client_credentials",
            "client_id": self.application_id,
            "client_secret": self.application_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }

        # Faz a requisição do token
        response = requests.post(url, data=data)
        response.raise_for_status()  # Levanta uma exceção para erros HTTP
        return response.json().get("access_token")

    def generate_embed_url(self):
        # Constrói a URL base de incorporação
        return f"https://app.powerbi.com/reportEmbed?reportId={self.report_id}&groupId={self.workspace_id}&autoAuth=true"

    def generate_iframe(self, access_token, width="800px", height="600px"):
        # Gera o iframe com a URL de incorporação e o token
        embed_url = self.generate_embed_url()
        iframe_html = (
            f'<iframe width="{width}" height="{height}" '
            f'src="{embed_url}" '
            f'frameborder="0" allowFullScreen="true" '
            f'sandbox="allow-same-origin allow-scripts allow-popups" '
            f'style="border:none;"></iframe>'
        )
        return iframe_html

    def get_embed_token(self):
        # Gera o token de incorporação
        access_token = self.get_access_token()
        # headers = {
        #     "Authorization": f"Bearer {access_token}",
        #     "Content-Type": "application/json"
        # }

        # url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/reports/{self.report_id}/GenerateToken"

        # body = {
        #     "accessLevel": "view",
        # }

        url = f"https://api.powerbi.com/v1.0/myorg/GenerateToken"
        headers = {"Authorization": f"Bearer {access_token}"}
        body = {
            "reports": [
                {
                    "id": self.report_id,
                }
            ],
            "targetWorkspaces": [
                {
                    "id": self.workspace_id
                }
            ],
            "accessLevel": "View"  # ou "Edit" dependendo do acesso necessário

        }

        response = requests.post(url, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        return response.json().get("token")

# Exemplo de uso:
powerbi = PowerBIEmbedder(
    application_id="750de238-6035-48a4-ae47-01ca6e55e53b",
    workspace_id="8d1c951b-5b2c-4903-9364-16788c518ab8",
    report_id="40a0a66c-d422-4c91-82ab-3c5171e16fad",
    application_secret="aiv8Q~j3Fc6J3H~eWRBF8vzQrrISnaFOcPpc7dvn",
    tenant_id="1345f5d4-b3ee-4534-bd31-b2cda5d2000d"
)

access_token = powerbi.get_access_token()
embed_token = powerbi.get_embed_token()
iframe_html = powerbi.generate_iframe(embed_token)
print(iframe_html)
