# Welcome to the Second Lab - Week 1, Day 3
# This lab focuses on working with various models and getting comfortable with APIs.

# Start with imports - ask ChatGPT to explain any package that you don't know
# Importing necessary libraries for file handling, environment variables, and API interactions.
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from IPython.display import Markdown, display

# Always remember to do this!
# Loading environment variables from the .env file to access API keys.
load_dotenv(override=True)
