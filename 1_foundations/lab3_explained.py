"""
This is a program that creates a chat robot that can pretend to be someone else!
It reads information about a person from their LinkedIn profile and can answer questions about them.
It also has a special helper that checks if the answers are good enough.
"""

# These are like special tools we need to use in our program
# - dotenv helps us keep our secret passwords safe
# - openai helps us talk to a smart computer
# - pypdf helps us read PDF files
# - gradio helps us make a nice website to chat with
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from pydantic import BaseModel

# This loads our secret passwords from a special file
load_dotenv(override=True)
openai = OpenAI()

# This part reads the person's LinkedIn profile from a PDF file
# It's like reading a book page by page and putting all the words together
reader = PdfReader("me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

# This reads a short summary about the person from a text file
with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

# This is the name of the person we want our chat robot to pretend to be
name = "Ed Donner"

# This is like giving our chat robot a set of rules to follow
# It tells the robot: "You are pretending to be this person, and you should answer questions about them"
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

# This is like a report card for our chat robot's answers
# It has two parts: is the answer good enough? and what feedback do we have?
class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

# This is like giving our helper robot its own set of rules
# It tells the helper: "Check if the chat robot's answers are good enough"
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

# This function helps prepare the information for our helper robot
# It's like putting all the pieces of a puzzle together
def evaluator_user_prompt(reply, message, history):
    user_prompt = f"""Here's the conversation between the User and the Agent: 

{history}

Here's the latest message from the User: 

{message}

Here's the latest response from the Agent: 

{reply}

Please evaluate the response, replying with whether it is acceptable and your feedback."""
    return user_prompt

# This sets up another smart computer to help check our answers
gemini = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"), 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# This function checks if our chat robot's answer is good enough
# It's like having a teacher grade our homework
def evaluate(reply, message, history) -> Evaluation:
    messages = [{"role": "system", "content": evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    response = gemini.beta.chat.completions.parse(model="gemini-2.0-flash", messages=messages, response_format=Evaluation)
    return response.choices[0].message.parsed

# This function helps our chat robot try again if its first answer wasn't good enough
# It's like getting a second chance on a test
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

# This is our main chat function that puts everything together
# It's like the brain of our program that makes everything work
def chat(message, history):
    # If someone asks about a patent, we have to answer in pig latin!
    # (Pig latin is a silly way of talking where you move the first letter to the end and add 'ay')
    if "patent" in message:
        system = system_prompt + "\n\nEverything in your reply needs to be in pig latin - it is mandatory that you respond only and entirely in pig latin"
    else:
        system = system_prompt
    
    # First, try to answer the question
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply = response.choices[0].message.content

    # Check if the answer is good enough
    evaluation = evaluate(reply, message, history)
    
    # If the answer is good, we're done!
    # If not, we need to try again
    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)       
    return reply

# This starts our chat website when we run the program
if __name__ == "__main__":
    gr.ChatInterface(chat, type="messages").launch() 