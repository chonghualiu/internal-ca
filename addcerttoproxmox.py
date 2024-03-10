#!/opt/homebrew/bin/python3
# (c) Martin Erzberger 2024
# Copies the required key / certificate to a proxmox instance
import argparse
import re
import json
import requests
from datetime import datetime

# Get the domain from the config file
pattern = re.compile("(?<=DOMAIN=).*")
domain = "undefined"
for i, line in enumerate(open('variables.sh', 'r')):
    for match in re.finditer(pattern, line):
        domain = match.group()
if domain == "undefined":
    print("Test your config file; There is no domain defined")
    exit(-1)
# Authentication
cacerts = "issuingca/certs/cacerts.pem"

# Parse the two mandatory arguments and setup the base URL
parser = argparse.ArgumentParser(description="Copy an ssl certificate and its private key to a proxmox host")
parser.add_argument('-p', '--rootpw', required=True, help="Password of the proxmox 'root' user")
parser.add_argument('-n', '--hostname', required=True, help='Hostname of the proxmox machine, without the domain')
args = parser.parse_args()
pwd = getattr(args, 'rootpw')
host = getattr(args, 'hostname')
baseurl = "https://" + host + "." + domain + ":8006/api2/json/"
certurl = "nodes/" + host + "/certificates/"

# Get a ticket cookie for authentication, see https://pve.proxmox.com/wiki/Proxmox_VE_API#Ticket_Cookie
# Note: Alternatively use a predefined API token, see https://pve.proxmox.com/wiki/Proxmox_VE_API#API_Tokens
data = {"username": "root@pam", "password": pwd}
response = requests.post(url=baseurl + "access/ticket", data=data, verify=cacerts)
if response.status_code != 200:
    print("Getting a ticket cookie failed with HTTP " + str(response.status_code))
    exit(-1)
# Extract the cookie from the response
responseData = response.json()['data']
ticket = {"PVEAuthCookie": responseData['ticket']}
token = responseData['CSRFPreventionToken']

# Get certificate info
response = requests.get(url=baseurl + certurl + "info", cookies=ticket, verify=cacerts)
if response.status_code != 200:
    print("Getting the certificates failed with HTTP " + str(response.status_code))
    exit(-1)
certs = response.json()['data']
for cert in certs:
    if "pveproxy-ssl.pem" == cert['filename']:
        ts = int(cert['notafter'])
        print("Found old certificate, valid until: " + datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))


# Replace the certificate
with open('issuingca/certs/' + host + "." + domain + '.cert.pem', 'r') as file:
    cert = file.read()
with open('rootca/certs/ca.cert.pem', 'r') as file:
    cert = cert + file.read()
with open('issuingca/private/' + host + "." + domain + '.key.open.pem', 'r') as file:
    key = file.read()
data = {"certificates": cert, "key": key, "restart": 1, "force": 1}
headers = {"Content-Type": "application/x-www-form-urlencoded", "CSRFPreventionToken": token }
response = requests.post(url=baseurl + certurl + "custom", headers=headers, data=data, cookies=ticket, verify=cacerts)
if response.status_code != 200:
    print("Updating the certificates failed with HTTP " + str(response.status_code))
    exit(-1)
cert = response.json()['data']
ts = int(cert['notafter'])
print("Installed new certificate, valid until: " + datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
