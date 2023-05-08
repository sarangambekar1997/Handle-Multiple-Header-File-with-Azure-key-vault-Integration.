import logging
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

os.environ["AZURE_CLIENT_ID"] = "8f546af4-bfd7-42a6-9bc0-01ec3429f042"
os.environ["AZURE_CLIENT_SECRET"] = "RiI8Q~q93-4WTIPK.5zCt.kXE8cNhG8fvgpTDaB4"
os.environ["AZURE_TENANT_ID"] = "8c3dad1d-b6bc-4f8b-939b-8263372eced6"


class GetSecrets:
    def __init__(self):
        self.__secret_client = SecretClient(
            vault_url="https://poccredaccess.vault.azure.net/",
            credential=DefaultAzureCredential()
        )

    def get_secrets(self):
        secret_dict = {}
        try:
            connection_string = self.__secret_client.get_secret("connectionstring").value
            container_name = self.__secret_client.get_secret("containername").value
        except Exception as e:
            logging.error("Error retrieving secrets: {}".format(str(e)))
            return None

        if connection_string is None or container_name is None:
            logging.error("Missing secrets")
            return None

        secret_dict.update({
            "connection_string": connection_string,
            "container_name": container_name
        })

        return secret_dict