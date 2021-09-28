#!/usr/bin/env python3

import urllib3
import requests
import json
import boto3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
#from bottle import route, run, post, request, static_file, error
import string
import random


username = "admin"
password = "Password123!"
headers= {}
payload = {}

def get_pod_start(id, dynamodb=None):
    # Get the access code for FlightSchool ID
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=False)
    # Query table for FlightSchool ID
    table = dynamodb.Table('cne_counter')
    response = table.get_item(
       Key={
            'id': id
        }
    )
    try:
    # try to parse the object    
        start_num = response['Item']['start_num']
    except:
        # If code not found, print an error
        return '''Error trying to find FlightSchool session ID'''
    else:
        #print("Found starting_pod_num %s" %(start_num))
        return(start_num)

def get_pod_end(id, dynamodb=None):
    # Get the access code for FlightSchool ID
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=False)
    # Query table for FlightSchool ID
    table = dynamodb.Table('cne_counter')
    response = table.get_item(
       Key={
            'id': id
        }
    )
    try:
    # try to parse the object    
        max_pods = response['Item']['max_pods']
    except:
        # If code not found, print an error
        return '''Error trying to find FlightSchool session ID'''
    else:
        #print("Found max_pods %s" %(max_pods)) 
        return(max_pods)


def get_cid(pod):
    ctrl_url = 'https://ctrl.pod'+str(pod)+str(".aviatrixlab.com/v1/api")
    payload = {"action": "login", "username": username, "password": password}
    payload_new = {}
    response = requests.post(url=ctrl_url, data=payload, verify=False)
    CID = response.json()["CID"]
    return CID

def vpc_lab2(cid, pod):
    cidr = "10."#+ str(pod_id.index(pod)+1)
    vpc_list = 'https://ctrl.pod'+str(pod)+str(".aviatrixlab.com/v1/api?action=list_custom_vpcs&CID=")+str(cid)+"&pool_name_only="
    vpc_response = requests.request("GET", vpc_list, headers=headers, data = payload, verify=False)
    vpcs = vpc_response.json()
    for i in vpcs['results']['all_vpc_pool_vpc_list']:
        if (cidr in i['vpc_cidr'] and i['cloud_type'] == 1 and i['avx_transit_vpc'] == True):
            transit_vpc = "pass"
        else:
            transit_vpc = "-"
    lab2_1 = "-"
    if (transit_vpc == "pass"):
        lab2_1 = "pass"
        #print('pod'+str(pod)+str(': 2.1: true'))
    #else:
        #print('pod'+str(pod)+str(': 2.1: false'))
    return(lab2_1)

def transit_gw_lab3(cid, pod):
    avtx_tgw_list = 'https://ctrl.pod'+str(pod)+str(".aviatrixlab.com/v1/api?action=list_aviatrix_transit_gateways&CID=")+str(cid)
    avtx_tgw_response = requests.request("GET", avtx_tgw_list, headers=headers, data = payload, verify=False)
    avtx_tgw = avtx_tgw_response.json()
    lab2_2 = "-"
    lab2_3 = "-"
    lab2_4 = "-"
    lab2_6 = "-"
    for i in avtx_tgw['results']:
        if ("aws" in i['name'].lower()):
            if ("aws" in i['name'] and 'activemesh' in i['ha_mode']):
                lab2_2 = "pass"
                if ("aws" in i['name'] and len(i['spoke_gw_list']) >= 2):
                    lab2_3 = "pass"
                    lab2_4 = "pass"
                    if ("aws" in i['name'] and len(i['transit_peer_list']) >= 2):
                        lab2_6 = "pass"
    
    return(lab2_2, lab2_3, lab2_4, lab2_6)

def s2c_tunnels(cid, pod):
    ctrl_url_show = "https://ctrl.pod"+str(pod)+".aviatrixlab.com/v1/api?action=list_site2cloud&CID="+str(cid)+"&transit_only="
    s2c_state = requests.request("GET", ctrl_url_show, headers=headers, data = {}, verify=False)
    s2c = s2c_state.json()
    lab2_7 = "-"
    for i in s2c['results']['connections']:
        if i['status'] == "Up":
            lab2_7 = "pass"

    #print('pod'+str(pod)+str(': 2.7: '+str(lab2_7)))

    return(lab2_7)
 
def security_domains(cid, pod):
    domain_name = []
    sec_domain_url = "https://ctrl.pod"+str(pod)+".aviatrixlab.com/v1/api?action=list_multi_cloud_security_domains&CID="+str(cid)
    sec_domain_url_req = requests.request("GET", sec_domain_url, headers=headers, data = {}, verify=False)
    sec_domain_url_resp = sec_domain_url_req.json()['results']['domains']
    lab3_1 = "-"
    lab3_2 = "-"
    lab3_3 = "-"
    for i in sec_domain_url_resp:
        domain_name.append(i['name'])
    try:
        if len(sec_domain_url_resp[0]['transit']) >= 3:
            lab3_1 = "pass"
    except:
        lab3_1 = "-"
 
    if len(sec_domain_url_resp) >= 4:
        lab3_2 = "pass"

    for i in domain_name:
        sec_domain_policy_url = "https://ctrl.pod"+str(pod)+".aviatrixlab.com/v1/api?action=get_multi_cloud_security_domain_details&CID="+str(cid)+"&domain_name="+str(i)
        sec_domain_policy_req = requests.request("GET", sec_domain_policy_url, headers=headers, data = {}, verify=False)
        sec_domain_policy_resp = sec_domain_policy_req.json()['results']
        if ("shared".lower() == sec_domain_policy_resp['name'].lower() and len(sec_domain_policy_resp['connected_domains']) >= 2):
            lab3_3 = "pass"
        else:
            pass

    return(lab3_1, lab3_2, lab3_3)

def security_attachment(cid, pod):
    attachment = []
    sec_domain_url = "https://ctrl.pod"+str(pod)+".aviatrixlab.com/v1/api?action=list_multi_cloud_security_domains&CID="+str(cid)
    sec_domain_url_req = requests.request("GET", sec_domain_url, headers=headers, data = {}, verify=False)
    sec_domain_url_resp = sec_domain_url_req.json()['results']['domains']
    for i in sec_domain_url_resp:
        attachment.append(i['attachment_count'])
    lab3_4 = "-"
    if sum(attachment) >=5:
        lab3_4 = "pass"

    return(lab3_4)

def fqdn_filter(cid, pod):
    fqdn_filter_list = 'https://ctrl.pod'+str(pod)+".aviatrixlab.com/v1/api?action=list_fqdn_filter_tags&CID="+str(cid)
    fqdn_filter_response = requests.request("GET", fqdn_filter_list, headers=headers, data = payload, verify=False)
    fqdn_filter = fqdn_filter_response.json()
    lab3_6 = "-"
    if fqdn_filter['results'] != {}:
        lab3_6 = "pass"

    return(lab3_6)


now = datetime.now()
id = "%s-%s-%s" % (now.year, '{:02d}'.format(now.month), '{:02d}'.format(now.day))
pod_start = get_pod_start(id)
pod_end = get_pod_end(id)

a="""<html><head>
  <script src="sorttable.js"></script>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
  <style>
  #t01 {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
    width: 100%;
  }
  
  #t01 td, #t01 th {
    border: 1px solid #ddd;
    padding: 8px;
  }
  
  #t01 tr:nth-child(even){background-color: #f2f2f2;}
  
  #t01 tr:hover {background-color: #ddd;}
  
  #t01 th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: #4CAF50;
    color: white;
  }
  </style></head>
  <table class="sortable" id="t01"><thead><tr><th>Pod ID</th><th>2.1</th><th>2.2</th><th>2.3</th><th>2.4</th><th>2.6</th><th>3.1</th><th>3.2</th><th>3.3</th><th>3.4</th><th>3.6</th></tr></thead>"""

print(a)
#print("<table><tr><td>Pod ID</td><td>2.1</td><td>2.2</td><td>2.3</td><td>2.4</td><td>2.6</td><td>3.1</td><td>3.2</td><td>3.3</td><td>3.4</td><td>3.6</td></tr>")
for pod in range(int(pod_start), int(pod_end)+1):
    pod_cid = (get_cid(pod))
    lab2_1 = vpc_lab2(pod_cid, pod)
    lab2_2 = transit_gw_lab3(pod_cid, pod)
    lab2_7 = s2c_tunnels(pod_cid, pod)
    lab3_1 = security_domains(pod_cid, pod)
    lab3_4 = security_attachment(pod_cid, pod)
    lab3_6 = fqdn_filter(pod_cid, pod)
    #print("Pod"+str(pod)+" 2.1: "+str(lab2_1)+" 2.2: "+str(lab2_2[0])+" 2.3: "+str(lab2_2[1])+" 2.4: "+str(lab2_2[2])+" 2.6: "+str(lab2_2[3])+" 3.1: "+str(lab3_1[0])+" 3.2: "+str(lab3_1[1])+" 3.3: "+str(lab3_1[2])+" 3.4: "+str(lab3_4)+" 3.6: "+str(lab3_6))
    print("<tr><td>Pod"+str(pod)+"</td><td>"+str(lab2_1)+"</td><td>"+str(lab2_2[0])+"</td><td>"+str(lab2_2[1])+"</td><td>"+str(lab2_2[2])+"</td><td>"+str(lab2_2[3])+"</td><td>"+str(lab3_1[0])+"</td><td>"+str(lab3_1[1])+"</td><td>"+str(lab3_1[2])+"</td><td>"+str(lab3_4)+"</td><td>"+str(lab3_6)+"</td></tr>")

print("</table></html>")