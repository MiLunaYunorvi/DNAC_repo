import requests
from requests.auth import HTTPBasicAuth
import datetime
DNAC_URL = "10.96.246.70"
DNAC_USER = "admin"
DNAC_PASS = "Cisco12345"

def get_auth_token():
    global hora_token
    """
    Building out Auth request. Using requests.post to make a call to the Auth Endpoint
    """
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL) # Endpoint URL
    hdr = {'content-type' : 'application/json'} # Define request header
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False) # Make the POST Request
    token = resp.json()['Token'] 
    print (token) # Retrieve the Token
    time_token = datetime.datetime.now()
    hora_token = time_token.strftime("%H:%M")
    return token # Create a return statement to send the token back for later use

print(get_auth_token())

while True:
    timenow = datetime.datetime.now()
    hora = timenow.strftime("%H:%M")
    if hora-hora_token >30:
        token=get_auth_token()
        print(get_auth_token)
    else:
        print('hola')

