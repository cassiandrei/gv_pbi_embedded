import datetime
from msal import ConfidentialClientApplication
import requests

class PowerBIService:
    def __init__(self):
        self.client_id = "750de238-6035-48a4-ae47-01ca6e55e53b"  # ID do Aplicativo
        self.client_secret = "aiv8Q~j3Fc6J3H~eWRBF8vzQrrISnaFOcPpc7dvn"  # Valor do segredo
        self.tenant_id = "1345f5d4-b3ee-4534-bd31-b2cda5d2000d"  # ID do Objeto (locatário)
        self.scope = ["https://analysis.windows.net/powerbi/api/.default"]
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.workspace_id = '8d1c951b-5b2c-4903-9364-16788c518ab8'
        self.app = ConfidentialClientApplication(
            self.client_id, self.client_secret, authority=self.authority
        )

    def get_access_token(self):
        token_response = self.app.acquire_token_for_client(scopes=self.scope)
        return token_response["access_token"]

    def generate_embed_token(self, access_token, dataset_id, report_id, workspace_id):
        url = f"https://api.powerbi.com/v1.0/myorg/GenerateToken"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "datasets": [
                {
                    "id": dataset_id,
                }
            ],
            "reports": [
                {
                    "id": report_id,
                }
            ],
            "targetWorkspaces": [
                {
                    "id": workspace_id
                }
            ],
            "accessLevel": "View"  # ou "Edit" dependendo do acesso necessário

        }
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        response.raise_for_status()
        return response.json()

    def test_acess_token(self):
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/reports"
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url=url, headers=headers)
        return response

    def get_token(self):
        teste_response = self.test_acess_token()
        print(teste_response, teste_response.status_code)

        # access_token = self.get_access_token()
        # report_id = 'o1p2q3r4-s5t6-7890-u123-v45678wxyz01'
        # workspace_id = 'a1b2c3d4-e5f6-7890-g123-h45678ijklmn'
        # dataset_id = 'cb197649-d5bc-4872-b61a-5161751cb34b'
        # return self.generate_embed_token(access_token, dataset_id, report_id, workspace_id)


