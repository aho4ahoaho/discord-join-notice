import discord
import ffmpeg
import os

appdir = os.path.dirname(os.path.abspath(__file__))

TrackList = []

class MusicPlayer:
    def __init__(self,client,voice_client):
        self.voice_client = voice_client
        self.client = client
        pass
    async def connect(self,member):
        # VoiceChannelへの入室必須
        if not member.voice:
            return
        # 投稿者と同じVoiceChannelに居ない場合は接続
        if not self.client.user in member.voice.channel.members:
            await member.voice.channel.connect(reconnect=True)

def scan_file():
    filelist = list()
    for p in os.scandir(appdir+"/track"):
        if p.is_file():
            filelist.append(".".join(p.name.split(".")[:-1]))
    TrackList.clear()
    TrackList.extend(filelist)
    return filelist

if __name__=="__main__":
    scan_file()
    print(TrackList)
    print(int(float(ffmpeg.probe(appdir+"/track/164.aac")["streams"][0]["duration"])*1000))