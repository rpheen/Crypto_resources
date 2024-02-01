'''
this file will loop through my strategy ideas
and then pass them to the ai to make a strategy
then it will pass the strategy to the backtester
this will loop forever and ever

- figure out how to loop through trading strategy ideas 
    - build an ai agent that comes up with a list of trading inidicator and combinations then outtputs to the strategy ai

2. be able to upload papers to the ai so it can make strats
    - read paper, do proccess, loop through all papers and do process
3. be able to upload a .py to the ai so it can make strats
    have a folder of papers it readds, and make a strat per
4. build a loop so it can make strats and backtestts 24/7
5. scrape websites
ai_trader5.py6. youtube videos,, download transcript to make strats
6. test with llms locally // look into lm studio 

- turn all my youtube vids to transcripts and fine tune llm so ppl can ask it questions

- david shaprio has a scrape code on his github on the way to agi 

- use the time as the output name



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

def extract_assistant_output(messages):
    output = ""
    for message in messages:
        if message.role == 'assistant' and hasattr(message.content[0], 'text'):
            output += message.content[0].text.value + "\n"
    return output.strip()

def create_and_run_assistant(name, instructions, model, content, filename):
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=model
    )
    print(f'Assistant {name} created....')
    save_assistant_id(assistant.id, filename=f"{filename}_id.txt")
    thread = client.beta.threads.create()
    print(f'Thread for {name} created...{thread.id}')
    save_assistant_id(thread.id, filename=f"{filename}_thread_id.txt")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=content
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
    return extract_assistant_output(messages.data)

def create_and_run_data_analysis(trading_idea):
    data_analysis_output = create_and_run_assistant(
        name='Data Analysis',
        instructions='Create a trading strategy based on the given trading idea.',
        model='gpt-4-1106-preview',
        content=f"Create a trading strategy using {trading_idea}. The strategy should be detailed enough for another AI to code a backtest.",
        filename='data_analysis'
    )
    if data_analysis_output:
        save_output_to_file(data_analysis_output, 'strategy', '/Users/tc/Dropbox/dev/github/Open-AI-Assistants/strategies', 'txt')
        return data_analysis_output
    else:
        print(f"No strategy output received for {trading_idea}.")
        return None

def create_and_run_backtest(strategy_output, trading_idea):
    if strategy_output:

        backtest_output = create_and_run_assistant(
            name='Backtest Analyst',
            instructions='Code a backtest for the provided trading strategy using backtesting.py, output only the code of the backtest',
            model='gpt-4-1106-preview',
            content=f"Strategy Output: {strategy_output}. Please use backtesting.py to code this strategy. YOUR MISSION IS TO TAKE THE STRATEGY AND CODE A BACKTEST USING BACKTEST.PY -- ONLY OUTPUT THE BACKTEST CODE",
            filename=f'backtest_{trading_idea}'
        )

        if backtest_output:
            save_output_to_file(backtest_output, f'bt_{trading_idea}', '/Users/tc/Dropbox/dev/github/Open-AI-Assistants/bt_code', 'py')
        else:
            print(f"No backtest output received for {trading_idea}.")
    else:
        print(f"No strategy output to backtest for {trading_idea}.")


# Trading ideas/topics list
trading_ideas = ['rsi + vwap', 'ema + bollinger', 'pivot lines', 'quarter theory', 'ichimoku', 'elliot waves', 'macd', 'adx', 'elliot waves + pivot lines', 'bollinger bands', 'sma + adx crossovers + bolinger band contraction + volume', 'grid trading + fibonacci']

# Loop through each trading idea
for idea in trading_ideas:
    print(f"Processing trading idea: {idea}")
    strategy_output = create_and_run_data_analysis(idea)
    create_and_run_backtest(strategy_output, idea)
