""" 
 IMPORTANT:

 Create a credentials.py file with the following vars: 
 
    MAILCHIMP_API_KEY = '' #INSTERT API KEY HERE
    MAILCHIMP_SERVER_PREFIX = '' #INSERT SERVER PREFIX HERE
    list_ID = "" #INSERT LIST ID HERE

    
 """

from flask import Flask, request, redirect, abort, url_for, Response
from flask_cors import CORS, cross_origin
from mailchimp_marketing.api_client import ApiClientError
import mailchimp_marketing as MCM
import hashlib, json, credentials, urllib, logging
import requests


URL_USED = 'http://localhost/'
logging.basicConfig(filename='app.log', level=logging.DEBUG)

def subscribeAnUnsubscribedUser(signup_email_hash, mailchimp):
    try:
        subscribe_response = mailchimp.lists.update_list_member(credentials.list_ID, signup_email_hash, body={
            "status": "subscribed"
        })
        logging.info(subscribe_response)
        return 'success'
    except ApiClientError as error:
        logging.error('ERROR: {}'.format(error.text)+ "FOR USER(hashed MD5) "+ signup_email_hash)
        return 'error'

def addLabelToUser(signup_email_hash, mailchimp):
    try:
        #Add newsletter tag to user
        tag_response = mailchimp.lists.update_list_member_tags(credentials.list_ID, signup_email_hash, body={
            "tags": [{
                "name": "newsletter",
                "status": "active"
            }]
        })
        logging.info(tag_response)
        return 'success'
    except ApiClientError as error:
        logging.error('ERROR: {}'.format(error.text) + "FOR USER (hashed MD5) "+ signup_email_hash)
        return 'error'

def addGivenNameToUser(signup_name, signup_email_hash, mailchimp):
    try:
        response = mailchimp.lists.update_list_member(credentials.list_ID, signup_email_hash, body={
            "merge_fields": {
                "NAME": signup_name
            }
        })
        logging.info(response)
        return 'success'
    except ApiClientError as error:
        logging.error('ERROR: {}'.format(error.text) + "FOR USER (MD5) "+ signup_email_hash)
        return 'error'

def connectToMailchimp():
    #Try connecting to mailchimp client
    try:
        mailchimp = MCM.Client()
        mailchimp.set_config({
            "api_key": credentials.MAILCHIMP_API_KEY,
            "server": credentials.MAILCHIMP_SERVER_PREFIX
        })
    except ApiClientError as error:
        logging.error('ERROR: {}'.format(error.text))
        return 'error'
    
    return mailchimp

## Get user's email if it exists
def getUserEmailFromMailChimp(email, email_hash, mailchimp):
    if(not email): 
        return False
    try:
        response = mailchimp.lists.get_list_member(credentials.list_ID, email_hash)
        logging.info(response)
        return 'success'
    except ApiClientError as error:
        logging.error('ERROR: {}'.format(error.text))
        return 'error'

## Check if the user is already subscribed
def checkIfSubscribed(mc_dat):
    if('status' in mc_dat and mc_dat['status'] == 'subscribed'):
        return True
    else:
        return False

def subscribeUser(signup_email, signup_name, mailchimp):
    user = {
        "email_address": signup_email,
        "status": "subscribed",
        "merge_fields": {
                "NAME": signup_name
        },
    }
    try:
        add_response = mailchimp.lists.add_list_member(credentials.list_ID, user)
        return (add_response)
    except ApiClientError as error:
        logging.error('ERROR: {}'.format(error.text) + "FOR USER "+ signup_email)
        return 'error'


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-type'

@app.route("/")
@cross_origin()
def helloWorld():
    return('HELLO')

@app.route('/signup', methods=['POST'])
@cross_origin()
def connectTo():
    return_vars = {}

    if(not hasattr(request, 'json') or not request.json.get('formData') or not request.json.get('formData').get('EMAIL') or not request.json.get('formData').get('NAME')):
        return_vars['missing_data'] = 'True'
        return Response(json.dumps(return_vars), status=404, mimetype='application/json')
    

    mailchimp = connectToMailchimp() #Establish connection
    signup_email = request.json.get('formData').get('EMAIL') #Get email from form
    signup_email_hash = hashlib.md5(signup_email.encode('utf-8')).hexdigest() #Get Email hash
    signup_name = request.json.get('formData').get('NAME') #Get name from form
    

    if("@" not in signup_email):
        return_vars['invalid_email'] = 'True'
        return Response(json.dumps(return_vars), status=400, mimetype='application/json')

    mc_dat = getUserEmailFromMailChimp(signup_email,signup_email_hash,mailchimp) #Get mailchimp respopnse
    
    if(mc_dat != False and mc_dat != 'error'): #if user exists in our contacts
        if(checkIfSubscribed(mc_dat)): #if user is already subscribed
            addLabelToUser(signup_email_hash, mailchimp)
            addGivenNameToUser(signup_name, signup_email, mailchimp)

            return_vars['already_subscribed'] = 'True'
            return Response(json.dumps(return_vars), status=200, mimetype='application/json')
        else:
            subscribeAnUnsubscribedUser(signup_email_hash, mailchimp)
            addLabelToUser(signup_email_hash, mailchimp)
            addGivenNameToUser(signup_name, signup_email_hash, mailchimp)
            return_vars['added_subscription'] = 'True'
            return Response(json.dumps(return_vars), status=201, mimetype='application/json')
    else:
        subscribeUser(signup_email, signup_name, mailchimp)
        addLabelToUser(signup_email_hash, mailchimp)

        return_vars['added_subscription'] = 'True'
        return Response(json.dumps(return_vars), status=201, mimetype='application/json')
    
    
    return Response(json.dumps(return_vars), status=302, mimetype='application/json')

    
@app.route('/calEvents', methods=['GET'])
def get_data():
    calendlyConnection = requests.get('https://calendly.com/api/v1/users/me/event_types', headers= {'X-TOKEN': credentials.CALENDLY_API_KEY})
    print(calendlyConnection.text)
    return('done')