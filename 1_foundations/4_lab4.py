# The first big project - Professionally You!
# This project introduces the Pushover tool for sending push notifications to your phone.

# imports
# Importing necessary libraries for environment variables, API interactions, and PDF handling.
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr

# The usual start
# Loading environment variables and initializing the OpenAI API client.
load_dotenv(override=True)
openai = OpenAI()

# For pushover
# Retrieving Pushover user and token from environment variables for sending notifications.
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

# Function to send a push notification
# This function takes a message as input and sends it to the Pushover API.
def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

# Function to record user details
# This function records the user's interest along with their email and notes, sending a notification.
def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

# Function to record unknown questions
# This function records any questions that couldn't be answered, sending a notification.
def record_unknown_question(question):
    push(f"Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}
