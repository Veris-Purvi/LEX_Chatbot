# LEX_Chatbot
## AWS Lambda Chatbot Backend

This repository contains a Python script that implements a serverless function using AWS Lambda. It serves as the backend for a chatbot, specifically designed to work with an Amazon Lex bot.

### Code Description

The code performs the following tasks:

1. Imports necessary libraries and modules, including `json`, `requests`, `pytz`, `datetime`, `slack_sdk`, and `boto3`.
2. Defines functions for interacting with AWS DynamoDB and Veris API.
3. The `store_id` function stores a user's email ID in a DynamoDB table named "Verified_Users".
4. The `check_id` function checks if a user's email ID exists in the DynamoDB table.
5. The `verify_email` function sends a verification email to a user using the Veris API.
6. The `lambda_handler` function is the entry point for the AWS Lambda function. It handles incoming requests from Amazon Lex and performs appropriate actions based on the intent and user input.
7. The code also includes functionality for scheduling meetings.
   - The `schedule_meeting` function receives input parameters such as meeting title, date, time, and participants.
   - It uses the provided information to schedule a meeting and store it in a database or send notifications to participants.
   - You can customize this function to integrate with your preferred meeting scheduling platform or notification mechanism.


### Usage

Once the AWS Lambda function is deployed and configured, it can be integrated with an Amazon Lex bot. The bot can then be used to interact with users and perform actions based on the intent and user input, including scheduling meetings.

To schedule a meeting using the chatbot:
1. Use the appropriate intent or command to initiate the meeting scheduling process.
2. Provide the required information such as the meeting  date, time, and participant by saying things like "Schedule meet with abc on 1st Aughust from 5PM to 6PM with Yash. It will then ask the misiing details and requirments accordingly.
3. The chatbot will invoke the `schedule_meeting` function, which will handle the scheduling process and notify participants if necessary.


