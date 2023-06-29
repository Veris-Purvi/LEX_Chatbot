import json
import requests
import pytz
import datetime
from slack_sdk import WebClient
from datetime import datetime
import boto3
import os

from dotenv import load_dotenv

load_dotenv('.env')
# Create a DynamoDB resource
client = boto3.client("dynamodb")
def store_id(email_id):
    response = client.put_item(
        TableName="Verified_Users",
        Item={
            "email":{"S": email_id}
           
        }
    )
def check_id(email_id):
    response = client.get_item(
    TableName="Verified_Users",
    Key={
        "email": {"S": email_id}
        }
    )
    if "Item" in response:
       return True
    else:
        return False


def send_otp(receiver_email):
    
    send_otp_url = 'https://local.veris.in/api/v4/validate-member-contact/'
    send_otp_payload = {
        "contact": receiver_email
        
    }
    requests.post(send_otp_url, json=send_otp_payload)
    return

def verify_otp(user_input,receiver_email):
    verify_otp_url = 'https://local.veris.in/api/v4/verify-member-otp/'
    verify_otp_payload = {
        "contact": receiver_email,
        "otp": int(user_input)
    }
    verify_otp_response = requests.post(verify_otp_url, json=verify_otp_payload)
    if verify_otp_response.status_code==200:
        return True
    else:
        return False
def convert_to_iso_format(date_str, time_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        dummy_date = datetime.strptime("2000-01-01 " + time_str, "%Y-%m-%d %H:%M")
        source_tz = pytz.timezone('Asia/Kolkata')
        localized_dummy_date = source_tz.localize(dummy_date)
        utc_date = localized_dummy_date.astimezone(pytz.utc)
        combined_datetime = datetime.combine(date_obj, utc_date.time())
        formatted_datetime = combined_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        return formatted_datetime
    except ValueError as e:
        return str(e)

def valid_venues(user_name):
    myToken = '97aeb12956cdfdf94a4a187f3b7a2c719203f8ff'
    url = "https://lbenz.veris.in/"

    username = user_name

    headers = {"Authorization": 'token {}'.format(myToken), "Content-Type": "application/json"}
    venue_params = {'q': username}

    orgId = 8
    venues = requests.get(f"{url}api/v2/organisation/{orgId}/venues/", headers = headers)
    venues_data = json.loads(venues.content)
    venue_names = [result["name"] for result in venues_data["results"]]
    return venue_names
def fetch_api_val(org_name, user_name, data):
    myToken = os.env['myToken']
    url = "https://lbenz.veris.in/"

    username = user_name
    
    headers = {"Authorization": 'token {}'.format(myToken), "Content-Type": "application/json"}
    venue_params = {'q': username}

    orgId = 8
    venues = requests.get(f"{url}api/v2/organisation/{orgId}/venues/", headers = headers)
    venues_data = json.loads(venues.content)
    venue_names = [result["name"] for result in venues_data["results"]]
    venue_id = None
    final_venue = data['venue'] + " (VMS)"
    for result in venues_data["results"]:
       
        if result['name'] == final_venue:
            venue_id = result['_id']
            break
    
    venue_params = {'q': username}
    
    hosts = requests.get(f"{url}/api/v4/organization/{orgId}/venue/{venue_id}/valid-hosts/",
                          headers= headers, params= venue_params)

    
    
    hosts_data = json.loads(hosts.content)
    

    host_id = None
    
    for result in hosts_data['results']:
        if username.lower() == result['first_name'].lower():
            
            host_id=(result['contact_id'])
            break
        
    payload = {
        "host": host_id,
        "venue": venue_id,
        "valid_from": convert_to_iso_format(data['date'],data['start_time']),
        "valid_till": convert_to_iso_format(data['date'],data['end_time']),
        "extra_instructions": "test",
        "do_not_notify_host": False,
        "do_not_notify_guest": False,
        "is_hierarchy_invite": False,
        "hierarchy_invites_detail": {
            "request_access": ["mobile"]
            },
        "guest": {
            "first_name" : data['first_name'],
            "last_name" : data['last_name'],
            "contacts": {"email" : data['contact']}
        },
        "meta": {
            "invite": "test"
        },
        "workflows": {
            "workflow_id": {},
            "workflow_data": {}
        }
    }

    try:
        response = requests.post(f"{url}/api/v4/organization/{orgId}/create-generic-invite/", 
                                 headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            
            return None
        else:
            return response.text
    except requests.exceptions.HTTPError as e:
            return e
            
def validate(slots,email,username):
    if not slots['Last_Name']:
      
        return {
            'isValid': False,
            'violatedSlot': 'Last_Name',
        }
        
    if not slots['emailaddress']:
        return {
            'isValid': False,
            'violatedSlot': 'emailaddress',
        }
    

    venue_options = valid_venues(username)
    venue_names = [option.rsplit(' ', 1)[0] for option in venue_options]
     
    if not slots['Venue']:   
       
        return {
            'isValid': False,
            'violatedSlot': None,
            'message':"Please select the Venue",
            'response_card' : {
           
                    "title": "Venues:",
                    "buttons": [
                        {
                            "text": option,
                            "value": option
                        }
                        for option in venue_names
                    ]
                }
            }


    if not slots['Date']:
        return {
            'isValid': False,
            'violatedSlot': 'Date'
        }
    if not slots['StartTime']:
        return {
            'isValid': False,
            'violatedSlot': 'StartTime'
        }

    if not slots['EndTime']:
        return {
            'isValid': False,
            'violatedSlot': 'EndTime'
        }
    if check_id(email) and not slots['send_otp'] :
        return {
            "isValid": True,
            "violatedSlot": None
        }
    elif not check_id(email):
        
        if slots['send_otp'] !=None:
            user_input = slots['send_otp']['value']['interpretedValue']
            if verify_otp(user_input,email):
                store_id(email)
                
                return {
                    
                    "isValid": False,
                    "violatedSlot": 'correct_otp'
                }
            else:
                
                return {
                    "isValid": False,
                    "violatedSlot": None,
                    "message": "OTP Verification failed. Please try again by typing 'End' and starting the conversation again."
                }
        else:
            send_otp(email)
            return {
                "isValid": False,
                "violatedSlot": "send_otp"
            }
   
   
    

    return {'isValid': True}

verified_users=[]
def lambda_handler(event, context):
    
 
    
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    if event['inputTranscript']=="End" or event['inputTranscript']=="end":
        intent="End"
    else:
        intent="Meet_scheduler"
    
    try:
        session_id_parts = event["sessionId"].split(":")
        user_id = session_id_parts[1]
    except Exception as e:
        user_id="AB"
    slack_token =os.eniros['slack_token']
    client = WebClient(token=slack_token)
    user_id2=event['sessionId']
    if intent=="End":
            
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Close"
                    },
                    "intent": {
                        "name": "End",
                        "state": "Fulfilled"
                    }
                },
                "messages": [
                    {
                        "contentType": "PlainText",
                        "content": "Your conversation has ended"
                    }
                ]
            }
            return response
    
    
    
    # Extract the username and email ID from the response
    username=""
    email=""
    if(user_id!="AB"):
        response = client.users_profile_get(user=user_id)
        if response["ok"]:
            email = response["profile"]["email"]
        response = client.users_info(user=user_id)
        if response["ok"]:
            user = response["user"]
            username = user["real_name"]
    else:
        username="Purvi"
        email="purvigandhi2002@gmail.com"
   
    
    validation_result = validate(event['sessionState']['intent']['slots'],email,"Anusha")

    if event['invocationSource'] == 'DialogCodeHook':
        if not validation_result['isValid']:
            if 'message' in validation_result and 'response_card' in validation_result:
            
                response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slotToElicit": "Venue"
                    },
                    "intent": {
                        "name": intent,
                        "slots": slots,
                        
                    }
                },
                "messages": [
                    {
                        "contentType": "PlainText",
                        "content": validation_result['message']
                    },
                    {
                        "contentType": "ImageResponseCard",
                        "imageResponseCard": validation_result['response_card']
                    }
                ]
            }

            elif 'message' in validation_result and 'response_card' not in validation_result :
               
                
                response = {
                    "sessionState": {
                        "dialogAction": {
                            'type': 'Close',
                            
                        },
                        "intent": {
                            'name': intent,
                            'slots': slots,
                            'state':"Failed"
                            }
                        },
                         "messages": [
                        {
                            "contentType": "PlainText",
                             "content": validation_result['message']
                        }
                    ]
                    
                
                        
                    }
                
        
            else:
                
                response = {
                    "sessionState": {
                        "dialogAction": {
                            'slotToElicit': validation_result['violatedSlot'],
                            "type": "ElicitSlot"
                        },
                        "intent": {
                            'name': intent,
                            'slots': slots
                        }
                    }
                }
            
            return response

        else:
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots
                    }

                }
            }
            return response

    if event['invocationSource'] == 'FulfillmentCodeHook':
        
            data = {
                'contact': slots['emailaddress']['value']['interpretedValue'],
                'venue': slots['Venue']['value']['interpretedValue'],
                'start_time': slots['StartTime']['value']['interpretedValue'],
                'end_time': slots['EndTime']['value']['interpretedValue'],
                'date': slots['Date']['value']['interpretedValue'],
                'first_name': slots['Person']['value']['interpretedValue'],
                'last_name':slots['Last_Name']['value']['interpretedValue']
            }
            
            
            result = fetch_api_val("", "Anusha", data)
        
            if result is None:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "type": "Close"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots,
                            "state": "Fulfilled"
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "Thanks, I have scheduled your meet"
                        }
                    ]
                }
            else:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "type": "Close"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots,
                            "state": "Failed"
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": f"Oops, an error has occurred while processing your reservation: {result}"
                        }
                    ]
                }
    
            return response