import requests

class PowerBIEmbedder:
    def __init__(
        self, application_id, workspace_id, report_id, application_secret, tenant_id
    ):
        self.application_id = application_id
        self.workspace_id = workspace_id
        self.report_id = report_id
        self.application_secret = application_secret
        self.tenant_id = tenant_id
        self.access_token = self.generate_access_token()
        self.embed_token = self.generate_embed_token()
        self.embed_url = self.generate_embed_url()

    def generate_access_token(self):
        """
        Gera um token de acesso usando o fluxo Client Credentials OAuth 2.0
        """
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.application_id,
            "client_secret": self.application_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }

        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao gerar o token de acesso: {response.status_code} - {response.text}"
            )

        return response.json()["access_token"]

    def generate_embed_token(self):
        """
        Gera o Embed Token para o relatório Power BI.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/reports/{self.report_id}/GenerateToken"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "accessLevel": "View",
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao gerar o Embed Token: {response.status_code} - {response.text}"
            )
        print("Embed Token Response:", response.json())
        return response.json()["token"]

    def generate_embed_url(self, width="800px", height="600px"):
        """
        Gera uma URL para embutir o relatório Power BI com o Embed Token.
        """
        return f"https://app.powerbi.com/reportEmbed?reportId={self.report_id}&groupId={self.workspace_id}"
