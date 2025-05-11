"""
Lab 3 - Building a Chat Interface with Quality Control
This script implements a chat interface that simulates a person based on their LinkedIn profile
and includes quality control mechanisms to ensure responses are appropriate.
"""

# Import required packages
# - dotenv: For loading environment variables from .env file
# - openai: For interacting with OpenAI's API
# - pypdf: For reading and extracting text from PDF files
# - gradio: For creating a web interface for the chat application
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from pydantic import BaseModel

# Load environment variables and initialize OpenAI client
# This loads API keys and other configuration from .env file
load_dotenv(override=True)
openai = OpenAI()

# Read and extract text from the LinkedIn PDF file
# This code reads each page of the PDF and concatenates the text
reader = PdfReader("me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

# Read the summary text file containing additional context
with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

# Set the name of the person being simulated
name = "Ed Donner"

# Create the system prompt for the chat model
# This prompt instructs the model to act as the specified person
# and provides context from their LinkedIn profile and summary
system_prompt = f"""You are acting as {name}. You are answering questions on {name}'s website, 
particularly questions related to {name}'s career, background, skills and experience. 
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. 
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. 
Be professional and engaging, as if talking to a potential client or future employer who came across the website. 
If you don't know the answer, say so.

## Summary:
{summary}

## LinkedIn Profile:
{linkedin}

With this context, please chat with the user, always staying in character as {name}."""

# Create a Pydantic model for evaluation results
# This defines the structure for evaluation feedback
class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

# Create the system prompt for the evaluator model
# This prompt instructs the model to evaluate responses based on quality and accuracy
evaluator_system_prompt = f"""You are an evaluator that decides whether a response to a question is acceptable. 
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. 
The Agent is playing the role of {name} and is representing {name} on their website. 
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. 
The Agent has been provided with context on {name} in the form of their summary and LinkedIn details. Here's the information:

## Summary:
{summary}

## LinkedIn Profile:
{linkedin}

With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."""

# Create a function to format the user prompt for the evaluator
# This combines the conversation history, latest message, and response for evaluation
def evaluator_user_prompt(reply, message, history):
    user_prompt = f"""Here's the conversation between the User and the Agent: 

{history}

Here's the latest message from the User: 

{message}

Here's the latest response from the Agent: 

{reply}

Please evaluate the response, replying with whether it is acceptable and your feedback."""
    return user_prompt

# Initialize the Gemini model for evaluation
# This sets up the model with the appropriate API key and base URL
gemini = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"), 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Define the evaluation function
# This function takes a reply, message, and history, then returns an Evaluation object
def evaluate(reply, message, history) -> Evaluation:
    messages = [{"role": "system", "content": evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    response = gemini.beta.chat.completions.parse(model="gemini-2.0-flash", messages=messages, response_format=Evaluation)
    return response.choices[0].message.parsed

# Define the rerun function for failed responses
# This function attempts to generate a better response when the initial one fails evaluation
def rerun(reply, message, history, feedback):
    updated_system_prompt = f"""{system_prompt}

## Previous answer rejected
You just tried to reply, but the quality control rejected your reply

## Your attempted answer:
{reply}

## Reason for rejection:
{feedback}

"""
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

# Define the enhanced chat function with evaluation and rerun capabilities
# This function includes quality control and can retry failed responses
def chat(message, history):
    # Special case: If the message contains "patent", require response in pig latin
    if "patent" in message:
        system = system_prompt + "\n\nEverything in your reply needs to be in pig latin - it is mandatory that you respond only and entirely in pig latin"
    else:
        system = system_prompt
    
    # Generate initial response
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply = response.choices[0].message.content

    # Evaluate the response
    evaluation = evaluate(reply, message, history)
    
    # If response passes evaluation, return it
    # Otherwise, try to generate a better response
    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)       
    return reply

# Launch the Gradio chat interface
if __name__ == "__main__":
    gr.ChatInterface(chat, type="messages").launch() 