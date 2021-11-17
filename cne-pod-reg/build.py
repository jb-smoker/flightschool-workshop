#!/usr/bin/env python3

import urllib3
import json
import boto3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
from bottle import route, run, post, request, static_file, error, auth_basic, template
import string
import random
from boto3.dynamodb.conditions import Key, Attr

def get_next_pod_id(id, name, email, company, start_time, code, dynamodb=None):
    # Get the next Pod ID of a FlightSchool class.  Max pods are 50
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=True)
    # Query table for FlightSchool ID
    table = dynamodb.Table('cne_counter')
    response = table.get_item(
       Key={
            'id': id
        }
    )
    print(response)
    try:
    # try to parse the object  
        start_num = response['Item']['start_num']  
        pod_num = response['Item']['pod_num']
        max_pods = response['Item']['max_pods']
    except:
        # FlightSchool date not found or pod num cannot be parsed
        print("Error parsing the pod number")
        return(0)
    else:
        # Increment Pod Counter
        pod_num=pod_num+1
        padded_pod_num = str(pod_num).zfill(3)
        add_pod(id, pod_num, start_num, max_pods, code)
        # Set User ID
        user_id = "%s-%s" %(id, padded_pod_num)
        # Add User to Pod History
        add_user(id, user_id, name, email, company, start_time)
        print("Added user %s to the pod history") %user_id
        return(pod_num)

def get_code(id, dynamodb=None):
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
        code = response['Item']['code']
    except:
        # If code not found, print an error
        return '''Error Access Code Not Found'''
    else:
        print("Found Code %s") %code
        return(code)

def get_max_pods(id, dynamodb=None):
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
        print("Found max_pods %s") %max_pods
        return(max_pods)

def add_pod(id, pod_num, start_num, max_pods, code, dynamodb=None):
    # Insert a new record in DynamoDB
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=True)

    table = dynamodb.Table('cne_counter')
    response = table.put_item(
       Item={
            'id': id,
            'pod_num': pod_num,
            'start_num': start_num,
            'max_pods': max_pods,
            'code': code
        }
    )

def add_user(id, user_id, name, email, company, start_time, dynamodb=None):
    # Insert a new record in DynamoDB
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=True)

    table = dynamodb.Table('cne_history')
    response = table.put_item(
       Item={
            'user_id': user_id,
            'id': id,
            'full_name': name,
            'company': company,
            'email': email,
            'start_time': start_time
        }
    )

# Access Code Generator
def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Log in details
def check(user, pw):
    # Check user/pw here and return True/False
    if user=="avxlabs" and pw=="Password123":
        return True
    else:
        return False


# Check if the user is already registered and has a POD
def check_for_existing_user(id, email_input):
    dynamodb = boto3.resource('dynamodb', 'eu-central-1', verify=False)
    table = dynamodb.Table('cne_history')
    #response = table.scan()
    response = table.scan(FilterExpression=Attr('user_id').begins_with(id) & Attr('email').eq(email_input))
    if response['Count'] == 0:
        print("[DEBUG] Existing user {} and ID {} not found".format(email_input, id))
        return(0)
    else:
        users=response['Items']
        print("[DEBUG] Searching for email {} and ID {}".format(email_input, id))
        for user in users:
            user_id = user['user_id']
            pod_id = user_id.split('-')
            print("[DEBUG] Found existing Pod ID {} with Email {}".format(pod_id, email_input))
            pod_id = str(int(pod_id[3]))
            return(pod_id)            


# Route for creating a new FlightSchool Session
@route('/new')
@auth_basic(check)
def server_static(filepath="new.html"):
    return static_file(filepath, root='./public/')

@route('/status')
@auth_basic(check)
def server_static(filepath="status.html"):
    return static_file(filepath, root='./public/')

## Route to create the new FlightSchool class + Access Code
@post('/newclass')
def process():
    offset = request.forms.get('offset')
    offset = int(offset) - 1
    max_pods = request.forms.get('max_pods')
    max_pods = int(offset) + int(max_pods)
    now = datetime.now()
    id = "%s-%s-%s" % (now.year, '{:02d}'.format(now.month), '{:02d}'.format(now.day))
    # POD Start time # %m/%d/%Y, %H:%M:%S
    now = now.strftime("%Y-%m-%dT%H:%M:%S")
    # Get a new Access Code
    code = id_generator()
    # Insert a new record in DynamoDB
    try:
        add_pod(id, offset, offset, max_pods, code)
    except:
        return '''<html>
        <head>
            <title>FlightSchool Pod Registration</title>
        </head>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">

        <center>
        <div class="jumbotron jumbotron-fluid">
        <div class="container" style="width:200px;">
        <img src="/static/logo.png" class="img-fluid">
        </div>
        </div>
        <div class="alert alert-danger" role="alert">Unable to update DB!</div>'''
    else:
        return '''<html>
        <head>
            <title>FlightSchool Pod Registration</title>
        </head>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">

        <center>
        <div class="jumbotron jumbotron-fluid">
        <div class="container" style="width:200px;">
        <img src="/static/logo.png" class="img-fluid">
        </div>
        </div>
        <div class="alert alert-primary" role="alert">New Access Code: %s</b></div>
        ''' %(code)


@route('/')
def server_static(filepath="index.html"):
    return static_file(filepath, root='./public/')


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./public/')


## Route to try to register user for a POD
@post('/doform')
def process():
    # Get the form vars
    #max_num_pods = 46
    domain = "aviatrixlab.com"
    name = request.forms.get('name')
    email = request.forms.get('email')
    company = request.forms.get('company')
    code = request.forms.get('code')

    #Get the current date and time
    now = datetime.now()
    id = "%s-%s-%s" % (now.year, '{:02d}'.format(now.month), '{:02d}'.format(now.day))

    build_code = get_code(id)
    max_num_pods = get_max_pods(id)

    if code == build_code:
        now = now.strftime("%Y-%m-%dT%H:%M:%S")

        # Check if user already registered
        pod_id = check_for_existing_user(id, email)
        pod_id = int(pod_id)
        # pod_id = 0 if the user is new 
        print("[DEBUG] Pod id = {}".format(pod_id))

        if pod_id == 0:
            # Get the next POD ID, if the user is not already registered
            pod_id = get_next_pod_id(id, name, email, company, now, code)
        
        if pod_id <= max_num_pods:
            # print a page to display pod info
            first_name = name.split(' ')
            return '''<html>
            <head>
                <title>FlightSchool Pod Registration</title>
            </head>
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">

            <center>
            <div class="jumbotron jumbotron-fluid">
            <div class="container" style="width:200px;">
            <img src="/static/logo.png" class="img-fluid">
            </div>
            </div>
            <div class="alert alert-primary" role="alert">Welcome <span style="text-transform:uppercase"><b>%s</b></span>!  You've been assigned <b>Pod %s</b></div>
            <br>
            <div class="row">
            <div class="col-sm-4">
                <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Remote Access Server</h5>
                    <p class="card-text">u: admin</p>
                    <p class="card-text">p: Password123</p>
                    <a target="_blank" rel="noopener noreferrer" href="https://web.pod%s.%s" class="btn btn-primary">Open Server</a>
                </div>
                </div>
            </div>
            <div class="col-sm-4">
                <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Aviatrix Controller</h5>
                    <p class="card-text">u: admin</p>
                    <p class="card-text">p: Password123!</p>
                    <a target="_blank" rel="noopener noreferrer" href="https://ctrl.pod%s.%s" class="btn btn-primary">Open Controller</a>
                </div>
                </div>
            </div>
            <div class="col-sm-4">
                <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Aviatrix Co-Pilot</h5>
                    <p class="card-text">u: admin</p>
                    <p class="card-text">p: Password123!</p>
                    <a target="_blank" rel="noopener noreferrer" href="https://cplt.pod%s.%s" class="btn btn-primary">Open Co-Pilot</a>
                </div>
                </div>
            </div>
            </div>
            <div class="row">
            <div class="col-sm-12">
                <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Lab Guide</h5>
                    <p class="card-text">Download the lab guide here</p>
                    <a target="_blank" rel="noopener noreferrer" href="http://cne-workshop.s3.eu-central-1.amazonaws.com/CNE+Lab+Guide+v0.9.7.pdf" class="btn btn-primary">Open Lab Guide</a>
                </div>
                </div>
            </div>
            </div>''' %(first_name[0], pod_id, pod_id, domain, pod_id, domain, pod_id, domain)
            
        else:
            # print a page to say that there are no more pods left
            return '''<html>
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">

            <center>
            <div class="jumbotron jumbotron-fluid">
            <div class="container" style="width:400px;">
            <img src="/static/logo.png" class="img-fluid">
            </div>
            </div>
            <div class="alert alert-danger" role="alert">No more pods left</div>'''
    else:
        # print a page to say that there are no more pods left
        return '''<html>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">

        <center>
        <div class="jumbotron jumbotron-fluid">
        <div class="container" style="width:400px;">
        <img src="/static/logo.png" class="img-fluid">
        </div>
        </div>
        <div class="alert alert-danger" role="alert">Wrong Access Code! Please try again</div>'''


## Route to list all people that have registered for a POD
@route('/list')
@auth_basic(check)
def getusers():
    #try:
        dynamodb = boto3.resource('dynamodb', 'eu-central-1', verify=False)
        table = dynamodb.Table('cne_history')
        response = table.scan()
        #print(response)
        return template('list', users=response['Items'])

    #if (response):
    #    return template('list', users=response['Items'])
    #else: 
    #    return HTTPResponse(status=204)



@error(404)
def error404(error):
    return '404 - the requested page could not be found'

@error(401)
def error401(error):
    return '401 - access is forbidden'

run(host='0.0.0.0', reloader=True, port=8080, debug=True)

