import base64
import json

import requests
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


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

        # Passo 1: Obtém o access token
        self.access_token = self.generate_access_token()

        # Passo 2: Obtém o gateway id
        self.gateway_id = "c500f1a3-f37d-46f0-b8ac-4a6dbb98d459"

        # Passo 3: Altera o owner do dataset
        self.update_dataset_owner()

        # Passo 4: Altera os paramêtros da conexão
        self.update_datasource_parameters(db_parameters)

        # Passo 5: Verifica se o dataset possui uma conexão com o gateway
        if self.has_gateway_connection(db_parameters):

            # Passo 5.1: Insere o dataset com a conexão que tem o gateway
            self.update_dataset_connection_gateway()

        # Passo 6: Obtém o Embed Token
        self.embed_token = self.generate_embed_token()

        # Passo 7: Obtém a URL para Embedar
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

    def update_dataset_owner(self):
        """
        Altera o owner do dataset para o usuário autenticado.
        """
        # URL para listar datasources do dataset
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets/{self.dataset_id}/Default.TakeOver"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao alterar o ownder do dataset: {response.status_code} - {response.text}"
            )

    def has_gateway_connection(self, db_parameters):
        """
        Verifica se o dataset possui uma conexão com o gateway.
        """
        # URL para listar datasources do dataset
        url = (
            f"https://api.powerbi.com/v1.0/myorg/gateways/{self.gateway_id}/datasources"
        )
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao obter os parâmetros de conexão do dataset: {response.status_code} - {response.text}"
            )
        connections_in_gateway: list = response.json()["value"]

        for connection in connections_in_gateway:
            connection_in_gateway: dict = json.loads(connection["connectionDetails"])
            if (
                connection_in_gateway["server"] == db_parameters["server"]
                and connection_in_gateway["database"] == db_parameters["database"]
            ):
                return True
        return False

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

        if not self.connection_details:
            raise Exception("Não foi possível obter os paramêtros de conexão")

        # Defina os novos parâmetros de conexão
        payload = {
            "updateDetails": [
                {
                    "datasourceSelector": {
                        "datasourceType": "PostgreSql",
                        "connectionDetails": {
                            "server": self.connection_details["server"],
                            "database": self.connection_details["database"],
                        },
                    },
                    "connectionDetails": {
                        "server": new_parameters["server"],
                        "database": new_parameters["database"],
                    },
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao atualizar credênciais da conexão: {response.status_code} - {response.text}"
            )

    def update_datasource_parameters(self, new_parameters):
        """
        Atualiza os parâmetros de conexão do dataset.
        """
        # URL para listar datasources do dataset
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets/{self.dataset_id}/Default.UpdateParameters"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # Defina os novos parâmetros de conexão
        payload = {
            "updateDetails": [
                {
                    "name": "server",
                    "newValue": new_parameters["server"],
                },
                {
                    "name": "database",
                    "newValue": new_parameters["database"],
                },
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao atualizar os parâmetros de conexão: {response.status_code} - {response.text}"
            )

    def get_gateway_public_key(self):
        """
        Obtém a chave pública do gateway.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/gateways/{self.gateway_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao obter os parâmetros de conexão do dataset: {response.status_code} - {response.text}"
            )
        response_json = response.json()
        return {
            "modulus": response_json["publicKey"]["modulus"],
            "exponent": response_json["publicKey"]["exponent"],
        }

    def update_dataset_connection_gateway(self):
        """
        Insere o Dataset à um Gateway.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets/{self.dataset_id}/Default.BindToGateway"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "gatewayObjectId": self.gateway_id,
            "datasourceObjectIds": ["5347dbfa-7497-4873-b27e-35bddf216a5b"],
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao atualizar ao setar o gateway ao dataset: {response.status_code} - {response.text}"
            )
