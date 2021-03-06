#slack needed libraries
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import os
#needed to get the environment variables
from dotenv import load_dotenv
from os.path import join, dirname
#Snowflake connecter
import json
import snowflake.connector
#excel library
from openpyxl import Workbook
#Function file
from functions import BOPUS_METRICS, VENDOR_ATP
import io

#needed to get the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ.get('SLACK_SIGNING_SECRET')
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
slack_client = SlackClient(slack_bot_token)


# #snowflake
# ctx = snowflake.connector.connect(
#     user = os.environ.get('snowflake_username'),
#     password=os.environ.get('snowflake_password'),
#     account='petco.us-east-1'
#         )
# cs = ctx.cursor()
# try:
#     cs.execute("SELECT current_version()")
#     one_row = cs.fetchone()
#     print(one_row[0])
# finally:
#     cs.close()
# #ctx.close()





# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        slack_client.api_call("chat.postMessage", channel=channel, text=message)


# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.api_call("chat.postMessage", channel=channel, text=text)



# Example reaction emoji echo
@slack_events_adapter.on("app_mention")
def app_mention(event_data):
    event = event_data["event"]
    print(event)
    #emoji = event["reaction"]
    channel = event["channel"]
    message=event["text"]
    command = message.split(' ')

    if command[1] == 'snowflake':
        slack_client.api_call("chat.postMessage", channel=channel, text="Working on your BOPUS file!")
        BOPUS_METRICS()
        with open('query_results\BOPUS_Metrics.xlsx', 'rb') as f:
            return slack_client.api_call(
                "files.upload",
                channels=channel,
                filename='BOPUS_Metrics.xlsx',
                title='BOPUS Metrics',
                initial_comment='Here is your snowflake file',
                file=io.BytesIO(f.read())
            )




    if command[1] == 'vendor':
        slack_client.api_call("chat.postMessage", channel=channel, text="Working on your vendor file!")
        VENDOR_ATP()
        with open('query_results\VENDOR_ATP.xlsx', 'rb') as f:
            return slack_client.api_call(
                "files.upload",
                channels=channel,
                filename='VENDOR_ATP.xlsx',
                title='Vendor ATP',
                initial_comment='Here is your Vendor ATP file',
                file=io.BytesIO(f.read())
            )






    elif command[1] == 'jira':
        return slack_client.api_call("chat.postMessage", channel=channel, text="https://petcoalm.atlassian.net/browse/PDOMS-"+command[2])
    
    elif command[1] == 'compiled' and command[2] == 'sprint' and command[3] == 'notes':
        return slack_client.api_call("chat.postMessage", channel=channel, text="https://petcoalm.atlassian.net/wiki/spaces/PDWEB/pages/679510035/Petco.com+Sprint+Notes")
        
        #slack_client.api_call("chat.postMessage", channel=channel, text=one_row[1][0])
    else:
        #Default message
        return slack_client.api_call("chat.postMessage", channel=channel, text="Maybe try to ask bot for snowflake? ")
    

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERrrrROR: " + str(err))

# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
slack_events_adapter.start(host='0.0.0.0' ,port=os.environ.get('PORT') , debug=False)