import visual         # using multi thredding the code will execute
import audio
import time
from concurrent.futures.thread import ThreadPoolExecutor
def audio():
    audio_based()

def visual():
    visual_based()

executor = ThreadPoolExecutor(max_workers=2)
a = executor.submit(audio)
b = executor.submit(visual)
