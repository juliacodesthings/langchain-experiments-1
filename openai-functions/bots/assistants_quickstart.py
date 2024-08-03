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


completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the check-in time?"}],
    
)

print(completion.choices[0].message)

def create_assistant(file):
    """
    You currently canot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name = "WhatsApp Airbnb Assistant",
        instructions= "You're a helpflu WhatsApp assistant that can assist guests that are staying in airbnbs",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
    return assistant

file = upload_file("../data/airbnb-faq.pdf")

file.id

