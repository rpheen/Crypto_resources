# file we upload may need to be a jsonl file 
# how would we convert this json l file from 
# maybe seperate the ais to run in seperate files so they can run all day
import dontshareconfig as d  # Contains the API key
from openai import OpenAI
import time

client = OpenAI(api_key=d.key)

def save_assistant_id(assistant_id, filename):
    filepath = f'ids/{filename}'
    with open(filepath, 'w') as file:
        file.write(assistant_id)

def save_file_id(file_id, filename):
    filepath = f'ids/{filename}'
    with open(filepath, 'w') as file:
        file.write(file_id)

def upload_file(filepath, purpose):
    print('uploading file...')
    with open(filepath, 'rb') as file:
        response = client.files.create(file=file, purpose=purpose)
    return response.id

def create_and_run_data_assistant(name, instructions, model, filepath, filename):
    # Upload the data file with the correct purpose
    file_id = upload_file(filepath, 'assistants')
    save_file_id(file_id, f"{filename}_file_id.txt")  # Save the file ID

    # Create the assistant
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=model, 
        file_ids=[file_id]
    )
    print(f'Assistant {name} created....')
    save_assistant_id(assistant.id, filename=f"{filename}_id.txt")

    # Create a thread
    thread = client.beta.threads.create()
    print(f'Thread for {name} created...{thread.id}')
    save_assistant_id(thread.id, filename=f"{filename}_thread_id.txt")

    # Add message to thread with explicit instruction to use OpenAI's API
    content = f"Please analyze This is just raw OHLCV data from the file with ID: {file_id} and based on it create a trading strategy that will work well on this data. dont give me a basic strategy, something with high ROI. this is just raw data, so you have to use your knowledge to find a strategy that may work for it. you can use your database or code and test a couple strategies. output the instructions for the strategy, assuming that another ai will then code the backtest. so output precise instructions for the other ai to build the backtest. THE ONLY OUTPUT YOU WILL MAKE IS THE STRATEGY INSTRUCTIONS FOR THE OTHER AI WHO WILL CODE THE BACKTEST. DO NOT OUTPUT ANYTHING ELSE. DO NOT CODE"

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=content,
        file_ids=[file_id]
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for the run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status in ['completed', 'failed', 'cancelled']:
            print(f'Run completed with status: {run_status.status}')
            break
        else:
            print(f'{name} run still in progress, waiting 5 seconds...')
            time.sleep(5)

    # Fetch and print the messages after the run is completed
    print(f'Run for {name} finished, fetching messages...')
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(f'Messages from the thread for {name}:')
    for message in messages.data:
        print(f'{message.role.title()}: {message.content[0].text.value}')

# Run The Data Guy Assistant
create_and_run_data_assistant(
    name='The Data Guy',
    instructions='Using OpenAIs API, access and analyze the file content to determine the best time to trade based on the data.',
    model='gpt-4-1106-preview',
    filepath='BTC-USD-15m-2022-1-01.csv',
    filename='data_guy'
)
