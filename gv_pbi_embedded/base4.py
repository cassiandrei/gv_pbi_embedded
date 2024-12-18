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
        self.access_token = self._generate_access_token()

    def _generate_access_token(self):
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
            "scope": "https://api.powerbi.com/.default",
        }

        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao gerar o token de acesso: {response.status_code} - {response.text}"
            )

        return response.json()["access_token"]

    def _generate_embed_token(self):
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
        return response.json()["token"]

    def generate_embed_iframe(self, width="800px", height="600px"):
        """
        Gera um iFrame para embutir o relatório Power BI com o Embed Token.
        """
        embed_token = self._generate_embed_token()
        report_url = f"https://app.powerbi.com/reportEmbed?reportId={self.report_id}&groupId={self.workspace_id}"
        iframe = (
            f'<iframe width="{width}" height="{height}" src="{report_url}" data-access-token="{embed_token}" frameborder="0" allowFullScreen></iframe>'
        )
        return iframe

# Exemplo de uso
if __name__ == "__main__":
    # Configuração com os dados de autenticação e relatório
    application_id = "750de238-6035-48a4-ae47-01ca6e55e53b"
    application_secret = "aiv8Q~j3Fc6J3H~eWRBF8vzQrrISnaFOcPpc7dvn"
    tenant_id = "1345f5d4-b3ee-4534-bd31-b2cda5d2000d"
    workspace_id = "8d1c951b-5b2c-4903-9364-16788c518ab8"
    report_id = "40a0a66c-d422-4c91-82ab-3c5171e16fad"

    # Instancia a classe
    embedder = PowerBIEmbedder(
        application_id, workspace_id, report_id, application_secret, tenant_id
    )

    # Gera o iFrame
    iframe_code = embedder.generate_embed_iframe(width="1200px", height="700px")
    print("Código do iFrame:")
    print(iframe_code)

