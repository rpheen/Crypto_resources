'''
From Docs - https://platform.openai.com/docs/assistants/overview

Assistants - These are the AI 
Threads - these are where convos happen 
Messages - these are the messages in the threads
'''

import dontshareconfig as d  # open ai key is in here like this key = 'jkklj;j'
from openai import OpenAI
import time 

client = OpenAI(api_key=d.key)


def save_assistant_id(assistant_id, filename="assistant_id.txt"):
    '''
    Saves the assistant ID to a specified file.
    Parameters:
        assistant_id: The unique ID of the assistant.
        filename: The name of the file where the assistant ID will be saved.
    '''
    with open(filename, 'w') as file:
        file.write(assistant_id)

# Create the assistant
assistant = client.beta.assistants.create(
    name='AI Trader',
    instructions='you are a quant researcher, find trading strategies for bitcoin',
    model='gpt-4-1106-preview'
)

print('Assistant created....')
# save the assistant id
save_assistant_id(assistant.id, filename="researcher_assistant_id.txt")

# Create a thread
thread = client.beta.threads.create()
print(f'Thread created...{thread.id}')

# save the thread id
save_assistant_id(thread.id, filename="thread_id.txt")

# add message to thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role='user',
    content='find me a bitcoin trading strategy on the 15 minute that outperforms buy and hold. use the Vwap and keltner channels in the strategy. only output the strategy in a format that a 2nd ai agent can read and then code a backtest')

# run the assistant 
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

while True:
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    if run_status.status in ['completed', 'failed', 'cancelled']:
        print(f'Run completed with status: {run_status.status}')
        break
    else:
        print('Run still in progress, waiting 5 seconds...')
        time.sleep(5)

# Fetch and print the messages after the run is completed
print('Run finished, fetching messages...')
messages = client.beta.threads.messages.list(thread_id=thread.id)
print('Messages from the thread:')
for message in messages.data:
    print(f'{message.role.title()}: {message.content[0].text.value}')