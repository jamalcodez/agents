# First let's do an import
# Importing the load_dotenv function from the dotenv module to load environment variables from a .env file.
from dotenv import load_dotenv

# Next it's time to load the API keys into environment variables
# This loads the environment variables from a .env file, allowing us to use sensitive information like API keys securely.
load_dotenv(override=True)

# Check the keys
# Importing the os module to access environment variables.
# Retrieving the OpenAI API key from the environment variables.
# If the key exists, we print a confirmation message; otherwise, we prompt the user to set it.
import os
openai_api_key = os.getenv('OPENAI_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set - please head to the troubleshooting guide in the guides folder")
    
# And now - the all important import statement
# Importing the OpenAI class from the openai module to interact with the OpenAI API.
# If you get an import error, refer to the troubleshooting guide.
from openai import OpenAI

# And now we'll create an instance of the OpenAI class
# Creating an instance of the OpenAI class to interact with the API.
# If you're not sure what it means to create an instance of a class, refer to the guides folder!
openai = OpenAI()

# Create a list of messages in the familiar OpenAI format
# This list will be used to send messages to the OpenAI API for processing.
messages = [{"role": "user", "content": "What is 2+2?"}]

# And now call it! Any problems, head to the troubleshooting guide
# Sending the message list to the OpenAI API and getting a response.
# Printing the response content to display the result of the API call.
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages
)

print(response.choices[0].message.content)
