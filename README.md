# Manual de Instruções para Embed Power BI usando Power BI Premium

Este manual é um guia passo a passo para embedar relatórios do Power BI em uma aplicação usando Power BI Premium. Ele cobre desde a criação de uma nova conta e confirmação de e-mail até a geração de embed tokens e a implementação do relatório no frontend.

---

## 1. Criação de um Tenant e Conta no Azure

### 1.1. Criar um Tenant no Azure
1. Acesse o portal do Azure.
2. Navegue até **Microsoft Entra ID**.
3. Clique em **Criar um diretório** e forneça um nome para o tenant.
4. Finalize o processo e selecione o diretório recém-criado.

### 1.2. Validar Domínio e Criar uma Nova Conta Administradora
1. Valide o domínio associado ao tenant:
   - Acesse **Domínios personalizados** no **Microsoft Entra ID**.
   - Clique em **Adicionar domínio personalizado** e insira o domínio desejado.
   - Siga as instruções para adicionar os registros DNS no provedor do domínio.
2. Crie uma nova conta:
   - Acesse **Usuários > Novo Usuário**.
   - Escolha a opção **Criar um usuário** e finalize o processo.

---

## 2. Configuração do Power BI Premium

### 2.1. Atribuir Licença Power BI Premium
1. Acesse **Microsoft Entra ID > Licenças > Atribuir Licenças**.
2. Atribua a licença **Power BI Premium Per User (PPU)** à nova conta criada.

### 2.2. Configurar o Workspace Premium
1. Acesse o **Power BI Service**.
2. Crie um novo workspace:
   - Clique em **Workspaces > Criar Workspace**.
   - Configure como **Premium Per User**.
3. Publique relatórios no workspace.

---

## 3. Configurações do Tenant no Power BI Admin Portal

### 3.1 Configuração do usuário

1. Certifique que o usuário  PPU possue a role "Fabric Administrator" na organização

### 3.1. Configurar Permissões do Tenant
1. Acesse o **Power BI Admin Portal**.
2. Navegue até **Tenant settings** e ajuste:
   - **Export data**: Ative.
   - **Publish to web**: Habilite se necessário.
   - **Allow service principals to use Power BI APIs**: Ative.
   - **Embed content in apps**: Habilite.

---

## 4. Registro do Aplicativo no Azure AD

### 4.1. Registrar o Aplicativo
1. Acesse **Microsoft Entra ID > App Registrations > New Registration**.
2. Preencha os campos:
   - Nome: Insira um nome.
   - Supported Account Types: Escolha **Accounts in this organizational directory only**.
3. Clique em **Registrar**.

### 4.2. Configurar Permissões do Aplicativo
1. Acesse **API Permissions > Add a Permission**.
2. Selecione **Power BI Service** e adicione:
   - **Report.ReadWrite.All**
   - **Content.ReadWrite.All**
   - **Workspace.Read.All**
   - **Workspace.Read.All**
3. Clique em **Grant Admin Consent for [Tenant Name]**.

### 4.3. Gerar Client Secret
1. Acesse **Certificates & Secrets > New Client Secret**.
2. Copie o Client Secret gerado.

---

## 5. Desenvolvimento do Backend, exempo em Django

### 5.1. Gerar Access Token e Embed Token
Exemplo de script Python para gerar tokens:

```python
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

```

---

## 6. Desenvolvimento do Frontend

### 6.1. Template HTML
```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Power BI Report</title>
    <!-- Incluindo o SDK do Power BI -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/powerbi-client/2.19.1/powerbi.min.js"></script>
</head>
<body>
    <h1>Relatório Power BI</h1>
    <!-- Contêiner para o relatório -->
    <div id="reportContainer" style="width: 1200px; height: 700px;"></div>

    <script>
        // Configuração do relatório
        const embedConfig = {
            type: "report",
            id: "{{ report_id }}", // Report ID enviado pelo backend
            embedUrl: "{{ embed_url }}", // Embed URL enviado pelo backend
            accessToken: "{{ embed_token }}", // Embed Token enviado pelo backend
            tokenType: 1, // 1 = Embed Token
            settings: {
                panes: {
                    filters: { visible: false }, // Ocultar filtros
                    pageNavigation: { visible: true } // Mostrar navegação de páginas
                },
                // Ajuste do campo background
                background: undefined // Deixa o SDK gerenciar o fundo
            }
        };

        // Obtendo o contêiner do relatório
        const reportContainer = document.getElementById("reportContainer");

        // Embutindo o relatório no contêiner
        window.powerbi.embed(reportContainer, embedConfig);
    </script>
</body>
</html>

```

### 6.2. View do Django
```python
def power_bi_view(request):
    application_id="750de238-6035-48a4-ae47-01ca6e55e53b"
    workspace_id="8d1c951b-5b2c-4903-9364-16788c518ab8"
    report_id="40a0a66c-d422-4c91-82ab-3c5171e16fad"
    application_secret="aiv8Q~j3Fc6J3H~eWRBF8vzQrrISnaFOcPpc7dvn"
    tenant_id="1345f5d4-b3ee-4534-bd31-b2cda5d2000d"
    powerbi = PowerBIEmbedder(
        application_id, workspace_id, report_id, application_secret, tenant_id
    )
    context = {
        "report_id": report_id,
        "embed_url": powerbi.embed_url,
        "embed_token": powerbi.embed_token,

    }
    return render(request, 'power_bi_embedded/power_bi_embed.html', context)

```

---

## 7. Teste e Debug

1. Acesse a página de relatório no navegador.
2. Use o console do navegador para verificar erros.
3. Ajuste configurações de token e permissões, se necessário.

---

Com este guia, você deve ser capaz de embedar relatórios do Power BI em sua aplicação. Para dúvidas, verifique logs e permissões no Azure AD e no Power BI Admin Portal.