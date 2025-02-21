import base64
import json
import requests
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


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

        # Passo 4: Obtem os parâmetros de conexão
        self.connection_details = self.get_connection_details()

        # Passo 5: Verifica se o dataset possui uma conexão com o gateway
        if self.has_gateway_connection(db_parameters):

            # Passo 5.1: Altera os paramêtros da conexão
            self.update_dataset_connection(db_parameters)

            # Passo 5.2: Insere o dataset com a conexão que tem o gateway
            self.update_dataset_connection_gateway()

        else:
            # Passo 5.3: Obtém a public_key do gateway
            self.gateway_public_key = self.get_gateway_public_key()

            # Passo 5.4: Insere uma nova conexão com o gateway
            self.create_connection_and_add_to_gateway(db_parameters)

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

    def encrypt_credentials(self, username, password, modulus_b64, exponent_b64):
        credentials = json.dumps({"username": username, "password": password})

        # Decodificando de base64 e convertendo para inteiro
        modulus_bytes = base64.b64decode(modulus_b64)
        exponent_bytes = base64.b64decode(exponent_b64)
        modulus = int.from_bytes(modulus_bytes, "big")  # Convertendo bytes para inteiro
        exponent = int.from_bytes(
            exponent_bytes, "big"
        )  # Convertendo bytes para inteiro

        public_key = RSA.construct((modulus, exponent), True)
        cipher = PKCS1_OAEP.new(public_key)

        encrypted_credentials = cipher.encrypt(credentials.encode())
        return base64.b64encode(encrypted_credentials).decode()

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

    def get_connection_details(self):
        """
        Obtem os parâmetros de conexão do dataset.
        """
        # URL para listar datasources do dataset
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets/{self.dataset_id}/datasources"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Erro ao obter os parâmetros de conexão do dataset: {response.status_code} - {response.text}"
            )
        return {
            "server": response.json()["value"][0]["connectionDetails"]["server"],
            "database": response.json()["value"][0]["connectionDetails"]["database"],
        }

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

    def get_gateway_public_key(self):
        """
        Obtém a chave pública do gateway corretamente.
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

        # Obtém os dados do JSON
        public_key_data = response.json()["publicKey"]

        modulus_b64 = public_key_data["modulus"]  # Modulus está em Base64
        exponent_b64 = public_key_data["exponent"]  # Exponent está em Base64

        # Decodifica os valores de Base64 para bytes
        modulus = int.from_bytes(base64.b64decode(modulus_b64), byteorder="big")
        exponent = int.from_bytes(base64.b64decode(exponent_b64), byteorder="big")

        # Gera a chave pública RSA correta
        public_numbers = rsa.RSAPublicNumbers(exponent, modulus)
        public_key = public_numbers.public_key(backend=default_backend())

        return public_key


    def create_connection_and_add_to_gateway(self, db_parameters):
        """
        Cria um novo DataSource no Power BI Gateway.

        :param db_parameters: Dicionário contendo 'server', 'database', 'username' e 'password'.
        """

        # Obtém a chave pública do gateway
        public_key = self.gateway_public_key
        if not public_key:
            raise Exception("Chave publica do gateway nao encontrada")

        # Verifica se a chave tem 2048 bits
        print('public_key.key_size = ', public_key.key_size)
        if public_key.key_size != 2048:
            raise ValueError(
                f"A chave pública tem tamanho inválido: {public_key.key_size} bits. Esperado: 2048 bits.")

        # Formata as credenciais JSON
        credentials_json = json.dumps({
            "username": db_parameters['credentials'].split(':')[0],
            "password": db_parameters['credentials'].split(':')[1]
        })

        # Criptografa as credenciais usando a chave pública
        encrypted_credentials = public_key.encrypt(
            credentials_json.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Converte para Base64
        credentials_base64 = base64.b64encode(encrypted_credentials).decode()

        # URL da API para criar um novo DataSource
        url = f"https://api.powerbi.com/v1.0/myorg/gateways/{self.gateway_id}/datasources"

        # Cabeçalhos da requisição
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # Payload da requisição
        payload = {
            "connectionDetails": json.dumps({
                "server": db_parameters["server"],
                "database": db_parameters["database"]
            }),
            "credentialDetails": {
                "credentialType": "Basic",
                "credentials": credentials_base64,
                "encryptedConnection": "Encrypted",
                "encryptionAlgorithm": "RSA-OAEP",
                "privacyLevel": "Organizational",
            },
            "datasourceName": db_parameters["database"],
            "datasourceType": "PostgreSql",
        }

        # Faz a requisição POST para criar o DataSource
        response = requests.post(url, headers=headers, json=payload)

        # Trata a resposta da API
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Erro ao criar DataSource: {response.status_code} - {response.text}")


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
