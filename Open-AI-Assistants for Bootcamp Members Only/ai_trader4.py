# this one has 3 AIs - 1 reads OHLCV data and comes up with a strategy
# 2nd one backtests the strategy
# 3rd one debugs the backtest

import dontshareconfig as d  # Contains the API key
from openai import OpenAI
import time
import re  # Import regular expressions for parsing outputs

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
    # Create the assistant
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=model,
        file_ids=file_ids
    )

    print(f'Assistant {name} created....')
    save_assistant_id(assistant.id, filename=f"{filename}_id.txt")

    # Create a thread
    thread = client.beta.threads.create()
    print(f'Thread for {name} created...{thread.id}')
    save_assistant_id(thread.id, filename=f"{filename}_thread_id.txt")

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=content,
        file_ids=file_ids
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
        # Check if the message content is text or something else
        if hasattr(message.content[0], 'text'):
            print(f'{message.role.title()}: {message.content[0].text.value}')
        else:
            print(f'{message.role.title()}: [Non-text content received]')

    # Return the output for further use
    # Make sure to check for text content before returning
    if hasattr(messages.data[-1].content[0], 'text'):
        return messages.data[-1].content[0].text.value  # Assuming the last message is the assistant's output
    else:
        print('The last message did not contain text content.')
        return None

def parse_output_for_next_assistant(output):
    """
    Parses the output of one assistant to extract only the necessary part for the next assistant.
    """
    # Example: Extract only the strategy part from the first assistant's output
    match = re.search(r'STRATEGY INSTRUCTIONS:(.*)', output, re.DOTALL)
    if match:
        return match.group(1).strip()  # Return only the matched part
    return output  # If no specific part is matched, return the whole output

# Data Analysis Assistant
file_id = upload_file('BTC-USD-15m-2022-1-01.csv', 'assistants')
data_analysis_output = create_and_run_assistant(
    name='Data Analysis',
    instructions='Analyze the provided data file and output a trading strategy.',
    model='gpt-4-1106-preview',
    content=f"Please analyze This is just raw OHLCV data from the file with ID: {file_id} and based on it create a trading strategy that will work well on this data. dont give me a basic strategy, something with high ROI. this is just raw data, so you have to use your knowledge to find a strategy that may work for it. you can use your database or code and test a couple strategies. output the instructions for the strategy, assuming that another ai will then code the backtest. so output precise instructions for the other ai to build the backtest. THE ONLY OUTPUT YOU WILL MAKE IS THE STRATEGY INSTRUCTIONS FOR THE OTHER AI WHO WILL CODE THE BACKTEST. DO NOT OUTPUT ANYTHING ELSE. DO NOT CODE",
    filename='data_analysis',
    file_ids=[file_id]
)

# Ensure data analysis output is text before proceeding
if data_analysis_output:
    parsed_data_analysis_output = parse_output_for_next_assistant(data_analysis_output)

    # Backtesting Assistant
    backtest_output = create_and_run_assistant(
        name='Backtest Analyst',
        instructions='Code a backtest for the provided trading strategy using backtesting.py, output only the code of the backtest',
        model='gpt-4-1106-preview',
        content=parsed_data_analysis_output + " Please use backtesting.py to code this strategy. YOUR MISSION IS TO TAKE THE STRATEGY AND CODE A BACKTEST USING BACKTEST.PY -- ONLY OUTPUT THE BACKTEST CODE",
        filename='backtest_analyst',
        file_ids=[file_id]
    )

    # # Ensure backtest output is text before proceeding
    # if backtest_output:
    #     parsed_backtest_output = parse_output_for_next_assistant(backtest_output)

    #     # Debugging Assistant
    #     create_and_run_assistant(
    #         name='Code Debugger',
    #         instructions='Debug the provided backtest code and save the final code to bt_code.',
    #         model='gpt-4-1106-preview',
    #         content=parsed_backtest_output + " Debug and ensure this code works perfectly. YOUR MISSION IS TO DEBUG THE BACKTESTING.PY Code AND OUTPUT THE FINAL CODE IN PYTHON",
    #         filename='code_debugger',
    #         file_ids=[file_id]
    #     )
