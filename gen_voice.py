import requests
import sys
import json
from os import getenv
from romantokana import englishkana

voicevox_url = getenv("VOICEVOX_URL")

def gen_voice(text:str):
    speaker=8
    #text = englishkana(text)

    query = requests.post(voicevox_url+'/audio_query', params={"speaker":speaker,"text":text})
    query = query.json()
    query["speedScale"] = 0.82
    query["volumeScale"] = 1.7
    query=json.dumps(query,ensure_ascii=False)
    print(query)
    gen_voice = requests.post(voicevox_url+"/synthesis",params={"speaker":speaker},data=query.encode("utf-8"))
    return gen_voice.content

def list_speakers():
    print(json.dumps(requests.get(voicevox_url+"/speakers").json(),indent=2,ensure_ascii=False))

if __name__=="__main__":
    with open("voice.wav","wb") as voice:
        voice.write(gen_voice(sys.argv[1]))
