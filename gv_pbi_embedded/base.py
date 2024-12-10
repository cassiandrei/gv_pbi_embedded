import datetime
from msal import ConfidentialClientApplication
import requests

class PowerBIService:
    def __init__(self):
        self.client_id = "009d3b51-c12b-43fa-948b-7186aeea38be"  # ID do Aplicativo
        self.client_secret = "wr08Q~Sk06~YagiTocAYPN_TDNJk8_hV2-k48b7-"  # Valor do segredo
        self.tenant_id = "8acfb8de-c4cb-4003-9abc-c8528e9bd03f"  # ID do Objeto (locatário)
        self.scope = ["https://analysis.windows.net/powerbi/api/.default"]
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.app = ConfidentialClientApplication(
            self.client_id, self.client_secret, authority=self.authority
        )

    def get_access_token(self):
        token_response = self.app.acquire_token_for_client(scopes=self.scope)
        return token_response["access_token"]

    def generate_embed_token(self, access_token, report_id, workspace_id):
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "accessLevel": "View",  # Permissão: 'View' ou 'Edit'
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_token(self):
        access_token = self.get_access_token()
        report_id = 'o1p2q3r4-s5t6-7890-u123-v45678wxyz01'
        workspace_id = 'a1b2c3d4-e5f6-7890-g123-h45678ijklmn'
        dataset_id = 'cb197649-d5bc-4872-b61a-5161751cb34b'
        return self.generate_embed_token(access_token, report_id, workspace_id)
