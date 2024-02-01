'''
text to speech will come in handy throughout this
options
alloy, echo, fable, onyx, nova, shimmer
'''

# import openai
from openai import OpenAI
import dontshareconfig as d 
from pathlib import Path


#tts 
client = OpenAI(api_key=d.key)

fp = Path('sample2.mp3')

response = client.audio.speech.create(
    model='tts-1', 
    voice='onyx',
    input="And that's a wrap! If you're not dizzy from all these ups and downs, you're officially crypto-coaster certified. Remember, in the world of digital coins, every day is a 'choose your own adventure' book. Choose wisely, or you might just end up with a sequel called 'The Mystery of the Vanishing Portfolio"
)
response.stream_to_file(fp)