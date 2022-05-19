from time import sleep
import requests
import json
from requests.auth import HTTPBasicAuth
import os
import sys
import keyword
import datetime
import sqlite3
import time 
from datetime import timedelta

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


def delta_min(time):
    variacion = timedelta(minutes=60)
    time = time + variacion
    return time

def get_auth_token_first():
    global token
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'} 
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
    token = resp.json()['Token']
    print (token)                                                      
    return token 
    
def get_auth_token():
    global hora_30
    global token
    global hora_actual
    #hora_actual = time_now()
    flag = False
    #hora_30 = delta_min(hora_actual)
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'}                                       
    while flag == False:
        #resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
        hora_actual = time_now()  
        flag = True
        if hora_actual > hora_30:
            resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
            hora_30 = delta_min(hora_actual)
            flag = False
            token = resp.json()['Token']
        print (token)                                                      
    return token 

def get_device_list():
    """
    Building out function to retrieve list of devices. Using requests.get to make a call to the network device Endpoint
    """
    token = get_auth_token() # Get Token
    dic = {}
    #token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZmIwMmM2MTQzZTBlZTAwYzYyZTI0NmEiLCJhdXRoU291cmNlIjoiaW50ZXJuYWwiLCJ0ZW5hbnROYW1lIjoiVE5UMCIsInJvbGVzIjpbIjVmYjAyYzYxNDNlMGVlMDBjNjJlMjQ2OSJdLCJ0ZW5hbnRJZCI6IjVmYjAyYzYxNDNlMGVlMDBjNjJlMjQ2NyIsImV4cCI6MTY1MjgxNTM4NywiaWF0IjoxNjUyODExNzg3LCJqdGkiOiIwMjU4Mzc3Ny0yOThhLTQ2MjctOGQwYS0wMThmMTc2NDZlYjciLCJ1c2VybmFtZSI6ImFkbWluIn0.XACLBBHIeIljLRk2NgVsuL6wNVk4zcUnas7pvcjSr4aRgqghCvkhjhQVLnw4kTldYYlamguX8QqtaL2xi0zGIu_1tbs_RyflS8-Jbx5jKiiCjJF1hU_adhdf8XVG8Oew36fE2I6Ts8leLGDvsM27D-Sgnz7OnTtldHw2EcbUQcKPXfwk_LyoL1hYW-KRYQAtoGjkonnprh7xAD-nbcykylpvOZqkJx1shmSf8HchYagomLRjrKmO5OtT3KHfQo79NJRYcp5vt4KjOIV8FOemYzOQcU2uI3EMiEBB81Y0FaRHGYnQ1yrHZZ6dj0o71mnUNGXoiYTDSdXdMj7UExxC4g'
    url = "https://{}/api/v1/network-device".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify= False)  # Make the Get Request
    device_list = resp.json()
    print("{0:25}{1:25}".format("hostname", "id"))
    for device in device_list['response']:
        print("{0:25}{1:25}".format(device['hostname'], device['id']))
        dic[device['hostname']] = device['id']
    poe_request(token,dic) # initiate command runner
    #print(dic)

def poe_request(token,dic):
    for name,id in dic.items():
        print("**** PARA EL {} *****".format(id))
        uuid = id
        url = "https://{}/api/v1/network-device/{deviceUuid}/poe".format(DNAC_URL,deviceUuid = uuid)
        hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
        respuesta = requests.get(url, headers=hdr, verify= False)  # Make the Get Request
        resp = respuesta.json()
        if 'errorCode' not in resp['response']:
            po_Allo = resp['response']['powerAllocated']
            if po_Allo == None:
                print("NADA")
            else:
                print(id,'\n')
                print(resp['response']['powerAllocated'])
                pwr_allocated = float(resp['response']['powerAllocated'])
                pwr_consumed = float(resp['response']['powerConsumed'])
                pwr_Remainig = float(resp['response']['powerRemaining'])
                pwr_consumed_perc = float(round(pwr_consumed*100/pwr_allocated,2))
                time = getTime()
                lista_para = [name, pwr_allocated,pwr_consumed,pwr_Remainig,pwr_consumed_perc,time]
                lista_espe = [pwr_allocated,pwr_consumed,pwr_Remainig,pwr_consumed_perc,time]            
                #print(resp)
                almacenar_db('General2',lista_para)
                almacenar_db_perdevice(name,lista_espe)
                
def getTime():
    timenow = datetime.datetime.now().isoformat(timespec='seconds')
    #fecha = timenow.strftime("%d-%m-%Y")
    #hora = timenow.strftime("%H:%M")
    print(timenow)
    return timenow

def time_now ():
    timenow = datetime.datetime.now()
    return timenow

def almacenar_db(device_uuid,s):
    #print(device_uuid)
    lista = [tuple(s)]
    print(lista)
    try:
        #cursor.execute("DELETE TABLE '53b2062f-a20a-4930-a888-2a43a2e1596d'")
        
        cursor.execute("CREATE TABLE '{}' (DeviceName TEXT,powerAllocated REAL, powerConsumed REAL, powerRemaining REAL, powerUsed'%' REAL ,SDate TIMESTAMP)".format(device_uuid))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?)".format(device_uuid),lista)
        #cursor.execute("INSERT INTO '{}' ({},{},{},{})".format(device_uuid,s[0],s[1],s[2,s[3]]))
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(device_uuid),type(s[4]))
        #cursor.execute("INSERT INTO '{}' VALUES ({},{},{},{})".format(device_uuid,s[0],s[1],s[2],s[3]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?)".format(device_uuid),lista)
        conexion.commit()
        
def almacenar_db_perdevice(name, s):
    lista = [tuple(s)]
    print(lista)
    try:
        #cursor.execute("DELETE TABLE '53b2062f-a20a-4930-a888-2a43a2e1596d'")
        
        cursor.execute("CREATE TABLE '{}' (powerAllocated REAL, powerConsumed REAL, powerRemaining REAL, powerUsed'%' REAL ,SDate TIMESTAMP)".format(name))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(name),lista)
        #cursor.execute("
        # INSERT INTO '{}' ({},{},{},{})".format(device_uuid,s[0],s[1],s[2,s[3]]))
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(name),type(s[4]))
        #cursor.execute("INSERT INTO '{}' VALUES ({},{},{},{})".format(device_uuid,s[0],s[1],s[2],s[3]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(name),lista)
        conexion.commit()
        
if __name__ == "__main__":
    global hora_actual
    global hora_30
    global token
    token = get_auth_token_first()
    hora_actual = time_now()
    hora_30 = delta_min(hora_actual)
    for i in range(0,20):
        conexion = sqlite3.connect("C:/Users/michluna/OneDrive - Cisco/Documents/dne-dna-code/dne-dna-code/intro-dnac/04_Cmd_Runner/POE.db")
        cursor = conexion.cursor()
        conexion.commit()
        get_device_list()
        conexion.close()
        sleep(400)


