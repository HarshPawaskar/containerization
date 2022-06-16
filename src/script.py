import os
import io
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient
from azure.keyvault.secrets import SecretClient

# ONLY FOR LOCAL TESTING #######################################
# os.environ['AZURE_TENANT_ID'] = "8cea0357-ddbd-4749-b22e-9a5827f8ceba"
# os.environ['AZURE_CLIENT_ID'] = "77c2f17b-70ef-4984-bae2-2f4c618d9908"
# os.environ['AZURE_CLIENT_SECRET'] ="-m78Q~lcWFJXCf2bA6w1nIdmudV7BYswPgLcObZc"
#############################################################

# Configuration
BLOB_account = 'containerizationsa'
BLOB_container = 'testcontainer'
BLOB_name = 'out.txt'

FS_fname = 'in.txt'

KV_account = 'containerizationkv'
KV_secret_name = 'testsecrets'

# Print datetime and environment variables
print(f'{datetime.now()}')
print(f'This is an environment variable: {os.environ.get("public1")}')
print(f'This is a secret environment variable: {os.environ.get("private1")}')

# Authenticate with Azure
# (1) environment variables, (2) Managed Identity, (3) User logged in in Microsoft application, ...
AZ_credential = DefaultAzureCredential()

# Retrieve primary key for blob from the Azure Keyvault
KV_url = f'https://{KV_account}.vault.azure.net'
KV_secretClient = SecretClient(vault_url=KV_url, credential=AZ_credential)
BLOB_PrimaryKey = KV_secretClient.get_secret(KV_secret_name).value

# Set the BLOB client
BLOB_CONN_STR = f'DefaultEndpointsProtocol=https;AccountName={BLOB_account};AccountKey={BLOB_PrimaryKey};EndpointSuffix=core.windows.net'
BLOB_client = BlobClient.from_connection_string(conn_str=BLOB_CONN_STR, container_name=BLOB_container, blob_name=BLOB_name)

# Read text-file from mounted fileshare and write to BLOB
with open(f'mnt/{FS_fname}', 'rb') as f:
    dataBytesBuffer = io.BytesIO(f.read())
    dataBytesBuffer.seek(0)
    print(str(dataBytesBuffer))
    BLOB_client.upload_blob(dataBytesBuffer, overwrite=True)
print(f'File successfully uploaded to blob')