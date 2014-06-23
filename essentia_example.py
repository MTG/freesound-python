import pyaudio, numpy, scipy,freesound, essentia, wave, wavio
from essentia.standard import *
from scipy.io.wavfile import *

CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
SIZE = 4

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    
    print("* recording (3 seconds)")
    frames = []
    audio = numpy.array([])
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        floats = numpy.fromstring(data, 'Float32')
        frames.append(data)
        audio = numpy.hstack((audio,floats))
    print("* done")
    stream.stop_stream()
    stream.close()
    p.terminate()
    write_file(frames,'recording.wav')
    return audio

def write_file(frames,fname):
    wf = wave.open(fname, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SIZE)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def extract_mfcc(audio):
    w = Windowing(type = 'blackmanharris62')
    spectrum = Spectrum()
    mfcc = essentia.standard.MFCC()
    mfccs =[]
    audio = essentia.array(audio)
    for frame in FrameGenerator(audio, frameSize = 2048 , hopSize = 1024):
        mfcc_bands, mfcc_coeffs = mfcc(spectrum(w(frame)))
        mfccs.append(mfcc_coeffs)
    mfccs = essentia.array(mfccs).T
    return mfccs

def query_by_voice():
    c = freesound.FreesoundClient()
    c.set_token("<YOUR_API_KEY_HERE>","token")
    d = record_audio()
    mfcc_frames = extract_mfcc(d);
    mfcc_mean=numpy.mean(mfcc_frames,1)    
    mfcc_var=numpy.var(mfcc_frames,1)   
    m =",".join(["%.3f"%x for x in mfcc_mean])
    v =",".join(["%.3f"%x for x in mfcc_var])
    
    results = c.content_based_search(target="lowlevel.mfcc.mean:"+m+" lowlevel.mfcc.var:"+v,\
            fields="id,name,url,analysis", descriptors="lowlevel.mfcc.mean,lowlevel.mfcc.var", \
            filter="duration:0 TO 3")

    for sound in results:
        print(sound.name)
        print(sound.url)
        print("--")
        
    
    return results
    
    
    