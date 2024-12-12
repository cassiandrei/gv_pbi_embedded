import requests
import json


class PowerBIEmbedder:
    def __init__(self, application_id, workspace_id, report_id, application_secret, tenant_id):
        self.application_id = application_id
        self.workspace_id = workspace_id
        self.report_id = report_id
        self.application_secret = application_secret
        self.tenant_id = tenant_id

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
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/reports/{self.report_id}/GenerateToken"

        body = {
            "accessLevel": "view",
            "identities": []  # Adicione aqui identities se for necessário para Row-Level Security
        }

        response = requests.post(url, headers=headers, data=json.dumps(body))

        # Log para depuração
        if response.status_code != 200:
            print("Erro na requisição GenerateToken:")
            print("Status Code:", response.status_code)
            print("Response:", response.text)

        response.raise_for_status()
        return response.json().get("token")


# Exemplo de uso:
powerbi = PowerBIEmbedder(
    application_id="0e8c2906-5218-4c4b-8ff3-4c1165078879",
    workspace_id="8a9d43bd-baa4-4884-9361-03b664cf3551",
    report_id="b465f0ac-f047-4404-b18d-d32a15d98bf7",
    application_secret="gAG8Q~iHgtSshl6DeH3FCtm0m56qJniyVk55CaXN",
    tenant_id="1345f5d4-b3ee-4534-bd31-b2cda5d2000d"
)

access_token = powerbi.get_access_token()
embed_token = powerbi.get_embed_token()
iframe_html = powerbi.generate_iframe(embed_token)
print(iframe_html)
