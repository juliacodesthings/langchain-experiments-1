import os
import shelve
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)


# -------
# UPLOAD FILE
# ---------


def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(file=open(path, "rb"), purpose="assistants")
    return file


file = upload_file("/Users/juliaanderson/langchain-experiments/data/airbnb-faq.pdf")

# -------
# CREATE ASSISTANT
# -------


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp Airbnb Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist guests that are staying in our Paris AirBnb. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools=[
            {
                "type": "file_search",
            },
            {
                "type": "code_interpreter",
            },
        ],
        # tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        # file_ids=[file.id],
        tool_resources={
            "code_interpreter": {
                "file_ids": [file.id],
            }
        },
    )
    return assistant


assistant = create_assistant(file)


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------


def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant()
    print(f"To {name}:", new_message)
    return new_message


# create thread and add message


# Check if there is already a thread_id for the wa_id

#     thread = client.beta.threads.create()
#     thread_id = thread.id

#         #Add message to thread
#     message = client.beta.threads.create(
#             thread_id=thread.id,
#             role="user",
#             content=message_body,
#     )

# message_body = "What's the check-in time?"


# ---------------------
# Run assistant
# -------------


def run_assistant():
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve("asst_ifBu0R8DbBDHyFB68Alg4vax")
    thread = client.beta.threads.retrieve("thread_iE9LLVwzWZCwiOUqAdgdTAMF")

    # Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for completion
    # https://platform.openai.com/docs/assistants/deep-dive/runs-and-run-steps
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    new_message = messages.data[0].content[0].text.value
    return new_message


# --------------------------------------------------------------
# Test assistant
# --------------------------------------------------------------

new_message = generate_response("What's the check in time?", "123", "John")
new_message = generate_response("What's the pin for the lockbox?", "456", "Sarah")

new_message = generate_response("What was my previous question?", "123", "John")

new_message = generate_response("What was my previous question?", "456", "Sarah")
