from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
api_key = os.environ['OPENAI_API_KEY']

print(os.getenv('OPENAI_API_KEY'))