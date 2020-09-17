from flask import Flask, request, redirect, abort, url_for
from mailchimp_marketing.api_client import ApiClientError
import mailchimp_marketing as MCM
import hashlib, json, credentials

##TODO:
# - redirect user back to page with codes
# - what to do if user doesn't exist in contact list (i.e. add user to contact list)
# - error handling for api client
# - sanitize inputs?
# - Add captcha to form

#Try connecting to mailchimp client
try:
    mailchimp = MCM.Client()
    mailchimp.set_config({
        "api_key": credentials.MAILCHIMP_API_KEY,
        "server": credentials.MAILCHIMP_SERVER_PREFIX
    })
except ApiClientError as error:
    print("Error: {}".format(error.text))

## Get user's email if it exists
def getUserEmailFromMailChimp(email, email_hash):
    if(not email): 
        return False
    try:
        response = mailchimp.lists.get_list_member(credentials.list_ID, email_hash)
        return response
    except ApiClientError as error:
        return 'error'

## Check if the user is already subscribed
def checkIfSubscribed(mc_dat):
    if('status' in mc_dat and mc_dat['status'] == 'subscribed'):
        return True
    else:
        return False

app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def connectTo():
    signup_email = request.form.get('EMAIL') #Get email from form
    signup_email_hash = hashlib.md5(signup_email.encode('utf-8')).hexdigest() #Get Email hash
    signup_name = request.form.get('NAME') #Get name from form

    mc_dat = getUserEmailFromMailChimp(signup_email,signup_email_hash) #Get mailchimp respopnse

    if(mc_dat != False or mc_dat != 'error'): #if user exists in our contacts
        if(checkIfSubscribed(mc_dat)): #if user is already subscribed
            try:
                #Add newsletter tag to user
                tag_response = mailchimp.lists.update_list_member_tags(credentials.list_ID, signup_email_hash, body={
                    "tags": [{
                        "name": "newsletter",
                        "status": "active"
                    }]
                })
                print('tag response {}'.format(tag_response))
            except ApiClientError as error:
                print("Error: {}".format(error.text))
                
            



    
    return('kewl')

    
