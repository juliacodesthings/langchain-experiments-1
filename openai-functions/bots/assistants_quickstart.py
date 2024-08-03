from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)


def upload_file(path):
    #Upload a file with an "assistants" purpose
    file = client.files.create(file=open(path, "rb"), purpose = "assistants")
    return file 


file = upload_file("/Users/juliaanderson/langchain-experiments/data/airbnb-faq.pdf")


#CREATE ASSISTANT#

# completion = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": "What's the check-in time?"}],
    
# )

# # print(completion.choices[0].message)

def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name = "WhatsApp Airbnb Assistant",
        instructions= "You're a helpful WhatsApp assistant that can assist guests that are staying in airbnbs",
        tools=[{"type":"file_search",}, {"type": "code_interpreter",}],
        model="gpt-4-1106-preview",
       # file_ids=[file.id],
    )
    return assistant


assistant = create_assistant(file)

#create thread and add message

def generate_response(message_body):
    thread = client.beta.threads.create()
    thread_id = thread.id
    
    #add message to thread
    message = client.beta.threads.messages.create(
        thread_id = thread_id,
        role="user",
        content=message_body,
    )
    
message_body = "What's the check-in time?"