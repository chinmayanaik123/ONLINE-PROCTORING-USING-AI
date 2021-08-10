def audio_based():
    # Audio from the microphone is recording and converted to text using Google's speech recognition API.
    # A different thread is used to call the API such that the recording portion is not disturbed a lot,
    # which processes the last one, appends its data to a text file and deletes it.
    # NLTK we remove the stopwods from that file.The question paper is taken whose stopwords are also removed and their contents are compared.
    # Finally, the common words along with its number are displayed.
    print("audio based proctoring..............")
    import speech_recognition as sr  
    import pyaudio
    import wave
    import time
    import threading
    import os

    import _pickle as cPickle           
    import speech_recognition as sr
    import pyttsx3
    with open("test.txt","w") as f:
        f.write("")
    ###################################################to give instructions to the test taker
    #     #to get user data 
    # r = sr.Recognizer()
    #     # Function to convert text to speech
    # def SpeakText(command):
    #     # Initialize the engine
    #     engine = pyttsx3.init()
    #     engine.say(command)
    #     engine.runAndWait()
    #     print("Instructions...")
    #         # use the microphone as source for input.
    # with sr.Microphone() as source2:	
    #     r.adjust_for_ambient_noise(source2, duration=0.2)
    #     ques="what is your name"
    #     SpeakText(ques)
    #     audio2 = r.listen(source2)         #it will take a input from mic

    #                                     # Using ggogle to recognize audio
    #     name = r.recognize_google(audio2)
       
    #     name = name.lower() 
    #     a="hai  and welcome again  "+name
    #     SpeakText(a)
    #     SpeakText("This is a proctored online exam , you are under the observation and the whole video will be recorded")
    #     SpeakText("we will track your every movements. ")
    #     b="please dont copy , try ur best.  all the best"+name
    #     SpeakText(b)
    #     print("..........")

    #############################################record audio and match with question paper
    """RATE" is the "sampling rate", i.e. the number of frames per second
    "CHUNK" is the (arbitrarily chosen) number of frames the (potentially very long) signals are split into in this example
    Yes, each frame will have 2 samples as "CHANNELS=2", but the term "samples" is seldom used in this context (because it is confusing)
    Yes, size of each sample is 2 bytes (= 16 bits) in this example
    Yes, size of each frame is 4 bytes
    Yes, each element of "frames" should be 4096 bytes. sys.getsizeof() reports the storage space needed by the Python interpreter, which is typically a bit more than the actual size of the raw data.
    """
    def read_audio(stream, filename):
        chunk = 1024                      # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16   # 16 bits per sample
        channels = 2
        fs = 44100                        # Record at 44100 samples per second
        seconds = 10                      # Number of seconds to record at once
        filename = filename
        frames = []                       # Initialize array to store frames
        
        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)
        
                                        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        # Stop and close the stream
        stream.stop_stream()
        stream.close()

    def convert(i):
        if i >= 0:
            sound = 'record' + str(i) +'.wav'
            r = sr.Recognizer()
            
            with sr.AudioFile(sound) as source:
                r.adjust_for_ambient_noise(source)
                print("Converting Audio To Text and saving to file.. . ") 
                audio = r.listen(source)
            try:
                value = r.recognize_google(audio)            # API call to google for speech recognition
                os.remove(sound)
                if str is bytes: 
                    result = u"{}".format(value).encode("utf-8")
                else: 
                    result = "{}".format(value)
    
                with open("test.txt","a") as f:
                    f.write(result)
                    f.write(" ")
                    f.close()
                    
            except sr.UnknownValueError:
                print("")
            except sr.RequestError as e:
                print("{0}".format(e))
            except KeyboardInterrupt:
                pass

    p = pyaudio.PyAudio()            # Create an interface to PortAudio
    chunk = 1024                     # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100

    def save_audios(i):
        stream = p.open(format=sample_format,channels=channels,rate=fs,
                    frames_per_buffer=chunk,input=True)
        filename = 'record'+str(i)+'.wav'
        read_audio(stream, filename)

    for i in range(30//10):                             # Number of total seconds to record/ Number of seconds per recording
        t1 = threading.Thread(target=save_audios, args=[i]) 
        x = i-1
        t2 = threading.Thread(target=convert, args=[x]) # send one earlier than being recorded
        t1.start() 
        t2.start() 
        t1.join() 
        t2.join() 
        if i==2:
            flag = True
    if flag:
        convert(i)
        p.terminate()


    from nltk.corpus import stopwords 
    from nltk.tokenize import word_tokenize 

    file = open("test.txt") ## Student speech file
    data = file.read()
    file.close()
    stop_words = set(stopwords.words('english'))   
    word_tokens = word_tokenize(data) ######### tokenizing sentence
    filtered_sentence = [w for w in word_tokens if not w in stop_words]  
    filtered_sentence = [] 
    
    for w in word_tokens:   ####### Removing stop words
        if w not in stop_words: 
            filtered_sentence.append(w) 

    ####### creating a final file
    f=open('final.txt','w')
    for ele in filtered_sentence:
        f.write(ele+' ')
    f.close()
        
    ##### checking whether proctor needs to be alerted or not
    file = open("question_paper.txt") ## Question file
    data = file.read()
    file.close()
    stop_words = set(stopwords.words('english'))   
    word_tokens = word_tokenize(data) ######### tokenizing sentence
    filtered_questions = [w for w in word_tokens if not w in stop_words]  
    filtered_questions = [] 
    
    for w in word_tokens:   ####### Removing stop words
        if w not in stop_words: 
            filtered_questions.append(w) 
            
    def common_member(a, b):     
        a_set = set(a) 
        b_set = set(b) 
        
        # check length  
        if len(a_set.intersection(b_set)) > 0: 
            return(a_set.intersection(b_set))   
        else: 
            return([]) 

    comm = common_member(filtered_questions, filtered_sentence)
    print('Number of common words spoken by test taker:', len(comm))
    print(comm)

    print("Done")
audio_based()
