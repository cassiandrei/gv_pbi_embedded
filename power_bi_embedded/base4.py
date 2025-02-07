import base64

import requests


class PowerBIEmbedder:
    def __init__(
        self,
        application_id,
        workspace_id,
        report_id,
        application_secret,
        tenant_id,
        dataset_id,
        db_parameters,
    ):
        self.application_id = application_id
        self.workspace_id = workspace_id
        self.report_id = report_id
        self.application_secret = application_secret
        self.tenant_id = tenant_id
        self.dataset_id = dataset_id
        self.access_token = self.generate_access_token()
        self.embed_token = self.generate_embed_token()
        self.embed_url = self.generate_embed_url()

        self.update_dataset_connection(db_parameters)

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
            "datasetId": self.dataset_id,  # Adicionando o dataset_id ao payload
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

    def string_to_base64(self, input_string):
        """
        Converte uma string para Base64.
        """
        # Encode a string para bytes
        bytes_string = input_string.encode("utf-8")
        # Codifica os bytes em Base64
        base64_bytes = base64.b64encode(bytes_string)
        # Converte os bytes Base64 para string
        base64_string = base64_bytes.decode("utf-8")
        return base64_string

    def update_dataset_connection(self, new_parameters):
        """
        Atualiza os parâmetros de conexão do dataset.
        """
        # URL para listar datasources do dataset
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets/{self.dataset_id}/Default.UpdateDatasources"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        credentials: str = new_parameters["credentials"]
        credentials_base64 = self.string_to_base64(credentials)

        # Defina os novos parâmetros de conexão
        payload = {
            "updateDetails": [
                {
                    "datasourceType": "PostgreSql",  # Altere conforme o tipo de fonte de dados
                    "connectionDetails": {
                        "server": new_parameters["server"],
                        "database": new_parameters["database"],
                    },
                    "credentialDetails": {
                        "credentialType": "Basic",
                        "credentials": credentials_base64,
                        "encryption": "None",
                    },
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao atualizar os parâmetros de conexão: {response.status_code} - {response.text}"
            )

        print("Atualização bem-sucedida:", response.json())
