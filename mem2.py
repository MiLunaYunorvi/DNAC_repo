from operator import lshift
from time import sleep
import requests
import json
from requests.auth import HTTPBasicAuth
import os
import sys
import keyword
import re
import datetime
import sqlite3

# Get the absolute path for the directory where this file is located "here"
here = os.path.abspath(os.path.dirname(__file__))

# Get the absolute path for the project / repository root
project_root = os.path.abspath(os.path.join(here, "../.."))

# Extend the system path to include the project root and import the env files
# sys.path.insert(0, project_root)

# import env_lab 

# DNAC_URL = env_lab.DNA_CENTER["host"]
# DNAC_USER = env_lab.DNA_CENTER["username"]
# DNAC_PASS = env_lab.DNA_CENTER["password"]

DNAC_URL = "10.96.246.70"
DNAC_USER = "admin"
DNAC_PASS = "Cisco12345"

"""   
    This code snippet will run execute operational commands across your entire network using Cisco DNA Center 
    Command Runner APIs
"""
#CONEXION AL DB y CURSOS


def get_auth_token():
    """
    Building out Auth request. Using requests.post to make a call to the Auth Endpoint
    """
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                      # Endpoint URL
    hdr = {'content-type' : 'application/json'}                                           # Define request header
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)      # Make the POST Request
    token = resp.json()['Token']  
    print (token)                                                        # Retrieve the Token
    return token    # Create a return statement to send the token back for later use


def get_device_list():
    """
    Building out function to retrieve list of devices. Using requests.get to make a call to the network device Endpoint
    """
    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZmIwMmM2MTQzZTBlZTAwYzYyZTI0NmEiLCJhdXRoU291cmNlIjoiaW50ZXJuYWwiLCJ0ZW5hbnROYW1lIjoiVE5UMCIsInJvbGVzIjpbIjVmYjAyYzYxNDNlMGVlMDBjNjJlMjQ2OSJdLCJ0ZW5hbnRJZCI6IjVmYjAyYzYxNDNlMGVlMDBjNjJlMjQ2NyIsImV4cCI6MTY1MjQ2MDAxMSwiaWF0IjoxNjUyNDU2NDExLCJqdGkiOiIwYjAxNGU0Yi1hOWMxLTQ3NGQtYjA5Yy02NzBlYjZlZmY1NjMiLCJ1c2VybmFtZSI6ImFkbWluIn0.JjsfNzi5_iBVGoqlp4AFnpAcOIJe9X9nDHz01GJADrdS4O3vZXpwDMKzRAUQCOICsNArvnbbqzN-J3cjovZoIiyUZjzsi9BF7mbED5qN1_mhiWYkDTEmu1Oy4Xy-ybXorTj3bMSGnXz5vzt6a56mo0xQqpzqSCDqPD38NqaJWMS6KEPGZdY2Ot5hkmN83HG6PWfCySyPobK559wGeMmR8yf58mBPpmy0zh8OAE9t_8suxsiMrvlpp4K70doolEu6mk_6yOQ8rZSjfGLOp0SiE-ibpHPf2uoLN973wPdM0ZklhJ0l0iIIVDT8tOIexnpLGwdzSNm1Qi8BVQTAn_Xxow'
    #token = get_auth_token()
    url = "https://{}/api/v1/network-device".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify= False)  # Make the Get Request
    device_list = resp.json()
    print("{0:25}{1:25}".format("hostname", "id"))
    for device in device_list['response']:
        print("{0:25}{1:25}".format(device['hostname'], device['id']))
        #initiate_cmd_runner(token,device['id']) # initiate command runner
    initiate_cmd_runner(token) # initiate command runner

def initiate_cmd_runner(token):
    ios_cmd = "show processes cpu | include one minute"
    device_id = str(input("Copy/Past a device ID here:"))
    print("executing ios command -->", ios_cmd)
    param = {
        "name": "Show Command",
        "commands": [ios_cmd],
        "deviceUuids": [device_id]
    }
    url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
    header = {'content-type': 'application/json', 'x-auth-token': token}
    response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
    #print (response.json())
    task_id = response.json()['response']['taskId']
    print("Command runner Initiated! Task ID --> ", task_id)
    print("Retrieving Path Trace Results.... ")
    get_task_info(task_id, token)


def get_task_info(task_id, token):
    url = "https://{}/api/v1/task/{}".format(DNAC_URL, task_id)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    task_result = requests.get(url, headers=hdr, verify= False)
    file_id = task_result.json()['response']['progress']
    if "fileId" in file_id:
        unwanted_chars = '{"}'
        for char in unwanted_chars:
            file_id = file_id.replace(char, '')
        file_id = file_id.split(':')
        file_id = file_id[1]
        print("File ID --> ", file_id)
    else:  # keep checking for task completion
        get_task_info(task_id, token)
    get_cmd_output(token, file_id)


def get_cmd_output(token,file_id):
    print("INICIO DE FUNCION")
    url = "https://{}/api/v1/file/{}".format(DNAC_URL, file_id)
    hdr = {'x-auth-token': token, 'content-type': 'application/json'}
    cmd_result = requests.get(url, headers=hdr, verify= False)
    result= json.dumps(cmd_result.json(), indent=4, sort_keys=True)
    device_uuid = json.loads(result)[0]['deviceUuid']
    print(result)
    if json.loads(result)[0]['commandResponses']["SUCCESS"]:
        print("PRUEBA",json.loads(result)[0]['commandResponses']["SUCCESS"]['show processes cpu | include one minute'])
        sentence = json.loads(result)[0]['commandResponses']["SUCCESS"]['show processes cpu | include one minute']
        s = [ float(str(s).replace('%','')) for s in re.findall('[0-9]+[%]', sentence)]
        fecha= getTime() 
        s.append(fecha)
        
        almacenar_db(device_uuid,s)

def getTime():
    timenow = datetime.datetime.now().isoformat(timespec='seconds')
    #fecha = timenow.strftime("%d-%m-%Y")
    #hora = timenow.strftime("%H:%M")
    print(timenow)
    return timenow

def almacenar_db(device_uuid,s):
    print(device_uuid)
    lista = [tuple(s)]
    print(lista)
    try:
        #cursor.execute("DELETE TABLE '53b2062f-a20a-4930-a888-2a43a2e1596d'")
        
        cursor.execute("CREATE TABLE '{}' (FiveSeconds REAL, Interrup FLOAT, OneMinute FLOAT, FiveMinutes REAL, SDate TIMESTAMP)".format(device_uuid))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(device_uuid),lista)
        #cursor.execute("INSERT INTO '{}' ({},{},{},{})".format(device_uuid,s[0],s[1],s[2,s[3]]))
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(device_uuid),type(s[0]))
        #cursor.execute("INSERT INTO '{}' VALUES ({},{},{},{})".format(device_uuid,s[0],s[1],s[2],s[3]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(device_uuid),lista)
        conexion.commit()
        
if __name__ == "__main__":
    for i in range(1,10):
        conexion = sqlite3.connect("C:/Users/michluna/OneDrive - Cisco/Documents/dne-dna-code/dne-dna-code/intro-dnac/04_Cmd_Runner/CPU_UTILIZATION1.db")
        cursor = conexion.cursor()
        conexion.commit()
        get_device_list()
        conexion.close()
        i+=1
        sleep(60)