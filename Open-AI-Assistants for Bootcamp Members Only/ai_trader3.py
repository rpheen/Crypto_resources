import dontshareconfig as d  # Contains the API key
from openai import OpenAI
import time

client = OpenAI(api_key=d.key)

def save_assistant_id(assistant_id, filename):
    '''
    Saves the assistant ID to a specified file.
    Parameters:
        assistant_id: The unique ID of the assistant.
        filename: The name of the file where the assistant ID will be saved.
    '''
    with open(filename, 'w') as file:
        file.write(assistant_id)

def create_and_run_assistant(name, instructions, model, content, filename):
    # Create the assistant
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=model
    )

    print(f'Assistant {name} created....')
    save_assistant_id(assistant.id, filename=f"{filename}_id.txt")

    # Create a thread
    thread = client.beta.threads.create()
    print(f'Thread for {name} created...{thread.id}')

    # Save the thread id
    save_assistant_id(thread.id, filename=f"{filename}_thread_id.txt")

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=content
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

    # Return the output for further use
    return messages.data[-1].content[0].text.value  # Assuming the last message is the assistant's output

# Research Assistant
research_output = create_and_run_assistant(
    name='Research Trader',
    instructions='Research trading strategies for Bitcoin on the 15-minute timeframe and prepare a strategy for backtesting.',
    model='gpt-4-1106-preview',
    content='Find me a Bitcoin trading strategy on the 15 minute timeframe that uses VWAP and Keltner channels.',
    filename='research_trader'
)

# Backtesting Assistant
backtest_output = create_and_run_assistant(
    name='Backtest Analyst',
    instructions='Backtest the provided Bitcoin trading strategy using backtesting.py and analyze its performance.',
    model='gpt-4-1106-preview',
    content=research_output + " Please use backtesting.py and output the full code.",  # Pass the strategy from Research Trader here
    filename='backtest_analyst'
)

# Debugging Assistant
create_and_run_assistant(
    name='Code Debugger',
    instructions='Debug the backtested trading strategy code and output it to a Python file.',
    model='gpt-4-1106-preview',
    content=backtest_output + " Please use backtesting.py and output the full code." + 'here is the original strategy for your refrence, remember you are taking in the code and just debugging to make sure it works,' + research_output,  # Pass the code and results from Backtest Analyst here
    filename='code_debugger'
)

# pass in the code assistnat to these too 