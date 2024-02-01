'''
DONE - this is 2 AIs - 1 reads OHLCV data and comes up with a strategy
2nd one backtests the strategy 

'''

import dontshareconfig as d
from openai import OpenAI
import time
import hashlib
from datetime import datetime

client = OpenAI(api_key=d.key)

# Common functions
def save_assistant_id(assistant_id, filename):
    filepath = f'ids/{filename}'
    with open(filepath, 'w') as file:
        file.write(assistant_id)

def save_file_id(file_id, filename):
    filepath = f'ids/{filename}'
    with open(filepath, 'w') as file:
        file.write(file_id)

def upload_file(filepath, purpose):
    print('Uploading file...')
    with open(filepath, 'rb') as file:
        response = client.files.create(file=file, purpose=purpose)
    return response.id

def create_and_run_assistant(name, instructions, model, content, filename, file_ids):
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=model,
        file_ids=file_ids
    )
    print(f'Assistant {name} created....')
    save_assistant_id(assistant.id, filename=f"{filename}_id.txt")
    thread = client.beta.threads.create()
    print(f'Thread for {name} created...{thread.id}')
    save_assistant_id(thread.id, filename=f"{filename}_thread_id.txt")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=content,
        file_ids=file_ids
    )
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
            print(f'{name} run still in progress, waiting 5 seconds...')
            time.sleep(5)
    print(f'Run for {name} finished, fetching messages...')
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(f'Messages from the thread for {name}:')
    for message in messages.data:
        if hasattr(message.content[0], 'text'):
            print(f'{message.role.title()}: {message.content[0].text.value}')
        else:
            print(f'{message.role.title()}: [Non-text content received]')
    return extract_assistant_output(messages.data)

def extract_assistant_output(messages):
    """
    Extracts only the assistant's output from the messages, excluding the user's input.
    """
    output = ""
    for message in messages:
        if message.role == 'assistant' and hasattr(message.content[0], 'text'):
            output += message.content[0].text.value + "\n"
    return output.strip()

def generate_filename(base, content, extension):
    hash_part = hashlib.md5(content.encode()).hexdigest()[:10]
    timestamp = datetime.now().strftime("%m-%d-%H-%M")
    return f'{base}_{hash_part}_{timestamp}.{extension}'

def save_output_to_file(output, base, directory, extension):
    if not output:
        print("No output to save.")
        return
    filename = generate_filename(base, output, extension)
    filepath = f'{directory}/{filename}'
    with open(filepath, 'w') as file:
        file.write(output)
    print(f"Output saved to {filepath}")

def create_and_run_data_analysis():
    file_id = upload_file('BTC-USD-15m-2022-1-01.csv', 'assistants')
    data_analysis_output = create_and_run_assistant(
        name='Data Analysis',
        instructions='Analyze the provided data file and output a trading strategy.',
        model='gpt-4-1106-preview',
        content=f"Please analyze This is just raw OHLCV data from the file with ID: {file_id} and based on it create a trading strategy that will work well on this data. dont give me a basic strategy, something with high ROI. this is just raw data, so you have to use your knowledge to find a strategy that may work for it. you can use your database or code and test a couple strategies. output the instructions for the strategy, assuming that another ai will then code the backtest. so output precise instructions for the other ai to build the backtest. THE ONLY OUTPUT YOU WILL MAKE IS THE STRATEGY INSTRUCTIONS FOR THE OTHER AI WHO WILL CODE THE BACKTEST. DO NOT OUTPUT ANYTHING ELSE. DO NOT CODE",
        filename='data_analysis',
        file_ids=[file_id]
    )
    if data_analysis_output:
        save_output_to_file(data_analysis_output, 'strategy', '/Users/tc/Dropbox/dev/github/Open-AI-Assistants/strategies', 'txt')
        return data_analysis_output
    else:
        print("No data analysis output received.")
        return None

def create_and_run_backtest(strategy_output):
    if strategy_output:
        file_id = upload_file('BTC-USD-15m-2022-1-01.csv', 'assistants')
        backtest_output = create_and_run_assistant(
            name='Backtest Analyst',
            instructions='Code a backtest for the provided trading strategy using backtesting.py, output only the code of the backtest',
            model='gpt-4-1106-preview',
            content=f"Strategy Output: {strategy_output}. Please use backtesting.py to code this strategy. YOUR MISSION IS TO TAKE THE STRATEGY AND CODE A BACKTEST USING BACKTEST.PY -- ONLY OUTPUT THE BACKTEST CODE",
            filename='backtest_analyst',
            file_ids=[file_id]
        )
        if backtest_output:
            save_output_to_file(backtest_output, 'bt', '/Users/tc/Dropbox/dev/github/Open-AI-Assistants/bt_code', 'py')
        else:
            print("No backtest output received.")
    else:
        print("No strategy output provided for backtesting.")

# Run the Data Analysis and Backtest Analyst Assistants
strategy_output = create_and_run_data_analysis()
create_and_run_backtest(strategy_output)
