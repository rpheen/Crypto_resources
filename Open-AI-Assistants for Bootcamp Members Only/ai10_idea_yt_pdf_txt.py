import dontshareconfig as d
from openai import OpenAI
import time
import hashlib
from datetime import datetime
import requests
from io import BytesIO
import PyPDF2
from youtube_transcript_api import YouTubeTranscriptApi

client = OpenAI(api_key=d.key)

def save_assistant_id(assistant_id, filename_base):
    max_filename_length = 255
    filename = f"{filename_base}_id.txt"
    if len(filename) > max_filename_length:
        allowed_length = max_filename_length - len("_id.txt")
        filename_base = filename_base[:allowed_length]
        filename = f"{filename_base}_id.txt"

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
    print(output)
    print(f"Output saved to {filepath}")

def extract_assistant_output(messages):
    output = ""
    for message in messages:
        if message.role == 'assistant' and hasattr(message.content[0], 'text'):
            output += message.content[0].text.value + "\n"
    return output.strip()

def create_and_run_assistant(name, instructions, model, content, filename_base):
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=model
    )
    print(f'{name} created....')
    save_assistant_id(assistant.id, filename_base)
    thread = client.beta.threads.create()
    print(f'Thread for {name} created...{thread.id}')
    save_assistant_id(thread.id, filename_base)
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
            print(f'{name} generating alpha...')
            time.sleep(5)
    print(f'Run for {name} finished, fetching messages...')
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return extract_assistant_output(messages.data)

def create_and_run_data_analysis(trading_idea):
    short_name = 'strategy_creator_ai'

    # Calculate the maximum length allowed for trading_idea
    fixed_text_length = len("Create a trading strategy using . The strategy should be detailed enough for another AI to code a backtest. output the instructions for the strategy, assuming that another ai will then code the backtest. so output precise instructions for the other ai to build the backtest. THE ONLY OUTPUT YOU WILL MAKE IS THE STRATEGY INSTRUCTIONS FOR THE OTHER AI WHO WILL CODE THE BACKTEST. DO NOT OUTPUT ANYTHING ELSE. DO NOT CODE")
    max_length = 32768 - fixed_text_length

    if len(trading_idea) > max_length:
        print(f"Trading idea too long, truncating to {max_length} characters.")
        trading_idea = trading_idea[:max_length]

    content = f"Create a trading strategy using {trading_idea}. The strategy should be detailed enough for another AI to code a backtest. output the instructions for the strategy, assuming that another ai will then code the backtest. so output precise instructions for the other ai to build the backtest. THE ONLY OUTPUT YOU WILL MAKE IS THE STRATEGY INSTRUCTIONS FOR THE OTHER AI WHO WILL CODE THE BACKTEST. DO NOT OUTPUT ANYTHING ELSE. DO NOT CODE"

    data_analysis_output = create_and_run_assistant(
        name='Strategy Creator AI',
        instructions='Create a trading strategy based on the given trading idea.',
        model='gpt-4-1106-preview',
        content=content,
        filename_base=short_name
    )
    if data_analysis_output:
        save_output_to_file(data_analysis_output, short_name, '/Users/tc/Dropbox/dev/github/Open-AI-Assistants/strategies', 'txt')
        return data_analysis_output
    else:
        print(f"No strategy output received for {trading_idea}.")
        return None

def create_and_run_backtest(strategy_output, trading_idea):
    short_name = 'backtest_coder_ai'
    filename_base = hashlib.md5(trading_idea.encode()).hexdigest()[:10]
    backtest_output = create_and_run_assistant(
        name='Backtest Coder AI',
        instructions='Code a backtest for the provided trading strategy using backtesting.py, output only the code of the backtest',
        model='gpt-4-1106-preview',
        content=f"Strategy Output: {strategy_output}. Please use backtesting.py to code this strategy. YOUR MISSION IS TO TAKE THE STRATEGY AND CODE A BACKTEST USING BACKTEST.PY -- ONLY OUTPUT THE BACKTEST CODE",
        filename_base=filename_base
    )
    if backtest_output:
        save_output_to_file(backtest_output, short_name, '/Users/tc/Dropbox/dev/github/Open-AI-Assistants/bt_code', 'py')
    else:
        print(f"No backtest output received for {trading_idea}.")


def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en'])
        return ' '.join([t['text'] for t in transcript.fetch()])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def get_pdf_text(url):
    try:
        response = requests.get(url)
        pdf = PyPDF2.PdfReader(BytesIO(response.content))
        text = ""
        for page in range(len(pdf.pages)):
            text += pdf.pages[page].extract_text() + "\n"
        return text
    except PyPDF2.errors.PdfReadError:
        print(f"Error reading PDF from {url}")
        return None

def process_trading_ideas(ideas_list):
    for idea in ideas_list:
        print(f"Processing trading idea: {idea}")
        strategy_output = create_and_run_data_analysis(idea)
        create_and_run_backtest(strategy_output, idea)

# Function to read the trading ideas from strat_ideas.txt
def read_trading_ideas_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Now call this function at the start to read in strat_ideas.txt
file_trading_ideas = read_trading_ideas_from_file('strat_ideas.txt')

# Process ideas from the file
process_trading_ideas(file_trading_ideas)

# Text-based trading ideas list
text_trading_ideas = ['rsi + vwap', 'ema + bollinger', 'pivot lines', 'quarter theory', 'ichimoku', 'elliot waves', 'macd', 'adx', 'elliot waves + pivot lines', 'bollinger bands', 'sma + adx crossovers + bolinger band contraction + volume', 'grid trading + fibonacci']

# YouTube video URLs list
yt_vids = ['https://www.youtube.com/watch?v=0e6Oml0L5UM', 'https://www.youtube.com/watch?v=PNlOeHduduc', 'https://www.youtube.com/watch?v=TSk0GJEV-74', 'https://www.youtube.com/watch?v=T4zKrDvdMuA', 'https://www.youtube.com/watch?v=9JEmsSItdt4', 'https://www.youtube.com/watch?v=rf_EQvubKlk', 'https://www.youtube.com/watch?v=NdHGgmG1asM', 'https://www.youtube.com/watch?v=jU2YQC7TC0k', 'https://www.youtube.com/watch?v=VI-rzf3nfJc', 'https://www.youtube.com/watch?v=LeMY0IKBiLU']

# PDF URLs list
pdf_list = ['https://d2saw6je89goi1.cloudfront.net/uploads/digital_asset/file/1177972/jrfm-13-00178-v2.pdf', 'https://arxiv.org/pdf/1907.03665.pdf', 'https://www.forexmentoronline.com/wp-content/uploads/2015/11/09-14.pdf', 'http://personales.upv.es/thinkmind/dl/conferences/cognitive/cognitive_2015/cognitive_2015_6_20_40112.pdf', 'https://premio-vidigal.inesc.pt/pdf/SimaoSarmentoMSc-resumo.pdf', 'https://people.scs.carleton.ca/~dmckenne/5704/Paper/Final_Paper.pdf', 'https://d2saw6je89goi1.cloudfront.net/uploads/digital_asset/file/1177975/Profitable_Momentum_Trading_Strategies_for_Individual_Investors.pdf', 'https://d2saw6je89goi1.cloudfront.net/uploads/digital_asset/file/1177971/2006-article-p201__1_.pdf']

# Process text-based trading ideas
process_trading_ideas(text_trading_ideas)

# Process YouTube video transcripts as trading ideas
yt_trading_ideas = []
for url in yt_vids:
    video_id = url.split('=')[-1]
    transcript = get_youtube_transcript(video_id)
    if transcript:
        yt_trading_ideas.append(transcript)
process_trading_ideas(yt_trading_ideas)

# Process PDF documents as trading ideas
pdf_trading_ideas = []
for url in pdf_list:
    pdf_text = get_pdf_text(url)
    if pdf_text:
        pdf_trading_ideas.append(pdf_text)
process_trading_ideas(pdf_trading_ideas)
