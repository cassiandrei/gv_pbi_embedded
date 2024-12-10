from gv_pbi_embedded.base import PowerBIService

objeto = PowerBIService()
response = objeto.get_token()
print(response)