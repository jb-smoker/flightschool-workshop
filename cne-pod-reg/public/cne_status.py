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
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=True)
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
        return(start_num+1)

def get_pod_end(id, dynamodb=None):
    # Get the access code for FlightSchool ID
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=True)
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

def get_pod_name(id, pod_id, dynamodb=None):
    # Get the access code for FlightSchool ID
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=True)
    # Query table for FlightSchool ID
    padded_pod_num = str(pod_id).zfill(3)
    # Set User ID
    user_id = "%s-%s" %(id, padded_pod_num)
    table = dynamodb.Table('cne_history')
    response = table.get_item(
       Key={
            'user_id': user_id
        }
    )
    try:
    # try to parse the object    
        full_name = response['Item']['full_name']
    except:
        # If code not found, print an error
        full_name=""
        return(full_name)
    else:
        #print("Found starting_pod_num %s" %(start_num))
        return(full_name)

def get_company(id, pod_id, dynamodb=None):
    # Get the access code for FlightSchool ID
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=True)
    # Query table for FlightSchool ID
    padded_pod_num = str(pod_id).zfill(3)
    # Set User ID
    user_id = "%s-%s" %(id, padded_pod_num)
    table = dynamodb.Table('cne_history')
    response = table.get_item(
       Key={
            'user_id': user_id
        }
    )
    try:
    # try to parse the object    
        company = response['Item']['company']
    except:
        # If code not found, print an error
        company=""
        return(company)
    else:
        #print("Found starting_pod_num %s" %(start_num))
        return(company)

def get_cid(pod):
    ctrl_url = 'https://ctrl.pod'+str(pod)+str(".aviatrixlab.com/v1/api")
    payload = {"action": "login", "username": username, "password": password}
    payload_new = {}
    response = requests.post(url=ctrl_url, data=payload, verify=False)
    CID = response.json()["CID"]
    return CID

def vpc_lab2(cid, pod):
    vpc_cidr = str("10.%s.40.0/23") %pod
    vpc_list = 'https://ctrl.pod'+str(pod)+str(".aviatrixlab.com/v1/api?action=list_custom_vpcs&CID=")+str(cid)+"&pool_name_only="
    vpc_response = requests.request("GET", vpc_list, headers=headers, data = payload, verify=False)
    vpcs = vpc_response.json()
    lab2_1 = "-"
    for i in vpcs['results']['all_vpc_pool_vpc_list']:
        if i['vpc_cidr'] == vpc_cidr:
            lab2_1 = "pass"
    return(lab2_1)

def transit_gw_lab3(cid, pod):
    avtx_tgw_list = 'https://ctrl.pod'+str(pod)+str(".aviatrixlab.com/v1/api?action=list_aviatrix_transit_gateways&CID=")+str(cid)
    avtx_tgw_response = requests.request("GET", avtx_tgw_list, headers=headers, data = payload, verify=False)
    avtx_tgw = avtx_tgw_response.json()
    vpc_cidr = str("10.%s.40.0/23") %pod
    for i in avtx_tgw['results']:
        if (vpc_cidr in i['vpc_cidr']):
            lab2_2 = "pass"
            lab2_3 = spoke_gw_lab(cid)
            if (len(i['spoke_gw_list']) >= 2):
                lab2_4 = "pass"
            else:
                lab2_4 = "-"
            if (len(i['transit_peer_list']) >= 2):
                lab2_6 = "pass"
            else:
                lab2_6 = "-"
            return(lab2_2, lab2_3, lab2_4, lab2_6)
    return("-", "-", "-", "-")

def spoke_gw_lab(cid):
    spoke_gw_list = 'https://ctrl.pod'+str(pod)+str(".aviatrixlab.com/v1/api?action=list_primary_and_ha_spoke_gateways&CID=")+str(cid)
    spoke_gw_response = requests.request("GET", spoke_gw_list, headers=headers, data = payload, verify=False)
    spoke_gws = spoke_gw_response.json()
    if (len(spoke_gws['results']) > 4):
        return("pass")
    else:
        return("-")

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
  <meta http-equiv="refresh" content="5">
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
  <table class="sortable" id="t01"><thead><tr><th>Pod ID</th><th>Name</th><th>Company</th><th>2.1 New Transit VPC</th><th>2.2 Aviatrix Transit GW</th><th>2.3 Spoke GWs</th><th>2.4 Attach Spoke GWs</th><th>2.6 Transit Peering</th><th>2.7 S2C to On-Prem</th><th>3.1 Enable Segmentation</th><th>3.2 Create Security Domains</th><th>3.3 Connection Policies</th><th>3.4 Add VPCs to Security Domains</th><th>3.6 FQDN Filtering</th></tr></thead>"""

print(a)
#print("<table><tr><td>Pod ID</td><td>2.1</td><td>2.2</td><td>2.3</td><td>2.4</td><td>2.6</td><td>3.1</td><td>3.2</td><td>3.3</td><td>3.4</td><td>3.6</td></tr>")
for pod in range(int(pod_start), int(pod_end)+1):
    full_name = get_pod_name(id, pod)
    company = get_company(id, pod)
    pod_cid = (get_cid(pod))
    lab2_1 = vpc_lab2(pod_cid, pod)
    lab2_2 = transit_gw_lab3(pod_cid, pod)
    lab2_7 = s2c_tunnels(pod_cid, pod)
    lab3_1 = security_domains(pod_cid, pod)
    lab3_4 = security_attachment(pod_cid, pod)
    lab3_6 = fqdn_filter(pod_cid, pod)
    print("<tr><td>Pod"+str(pod)+"</td><td>"+str(full_name)+"</td><td>"+str(company)+"</td><td>"+str(lab2_1)+"</td><td>"+str(lab2_2[0])+"</td><td>"+str(lab2_2[1])+"</td><td>"+str(lab2_2[2])+"</td><td>"+str(lab2_2[3])+"</td><td>"+str(lab2_7)+"</td><td>"+str(lab3_1[0])+"</td><td>"+str(lab3_1[1])+"</td><td>"+str(lab3_1[2])+"</td><td>"+str(lab3_4)+"</td><td>"+str(lab3_6)+"</td></tr>")

print("</table></html>")
