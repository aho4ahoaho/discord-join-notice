import discord
from discord import Client, Member, Guild
import ffmpeg
import os
import random
from asyncio import sleep
from time import time
from typing import Union

appdir = os.path.dirname(os.path.abspath(__file__))

TrackList = []


class MusicPlayer:
    def __init__(self, client: Client, guild: Guild, volume: float = 1):
        self.client = client
        self.guild = guild
        self.volume = volume
        self.timeStamp = 0
        self.queue = random_track()
        self.index = 0
        pass

    async def connect(self, member: Member):
        # VoiceChannelへの入室必須
        if not member.voice:
            return
        # 投稿者と同じVoiceChannelに居ない場合は接続
        if not self.client.user in member.voice.channel.members:
            await member.voice.channel.connect(reconnect=True)

    async def disconnect(self):
        voice_client = self.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.disconnect()
        voice_client.cleanup()

    def random(self):
        self.queue = random_track()

    def now_playing(self) -> Union[str, None]:
        if self.index > 0:
            return self.queue[self.index-1]
        else:
            return None
        
    def get_playlist(self, all: bool = False):
        return self.queue

    def play(self, sound_path: str, volume: float = -1):
        if volume == -1:
            volume = self.volume
        voice_client = self.guild.voice_client
        self.timeStamp = time()
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(sound_path), volume=self.volume))

    def stop(self):
        voice_client = self.guild.voice_client
        self.timeStamp = time()
        if voice_client.is_playing():
            voice_client.stop()

    async def resume(self):
        if self.index > 0:
            self.index -= 1
        await self.playlist()

    async def previous(self):
        if self.index > 1:
            self.index -= 2
        await self.playlist()

    async def playlist(self):
        while True:
            # キューの最後まで再生したらキューを更新する
            if len(self.queue) == self.index:
                self.queue = random_track()
                self.index = 0

            # キューから曲を取り出す
            track = self.queue[self.index]
            self.index += 1
            # パスを作る
            track_path = appdir+"/track/"+track+".aac"
            # 曲を再生する
            self.play(track_path)
            # 自分が再生した曲を覚える
            timeStamp = time()
            self.timeStamp = timeStamp

            # 曲の長さを取得する
            track_len = float(ffmpeg.probe(track_path)[
                "streams"][0]["duration"])
            # 曲の長さだけスリープする
            await sleep(track_len)

            while self.timeStamp == timeStamp and (not self.guild.voice_client is None) and self.guild.voice_client.is_playing():
                await sleep(3)

            # 現在再生している曲が自分だったら次の曲を流す
            if self.timeStamp != timeStamp:
                break


def random_track():
    return random.sample(TrackList, len(TrackList))


def scan_file():
    filelist = list()
    for p in os.scandir(appdir+"/track"):
        if p.is_file():
            filelist.append(".".join(p.name.split(".")[:-1]))
    TrackList.clear()
    TrackList.extend(sorted(filelist))
    return filelist


if __name__ == "__main__":
    scan_file()
    print(TrackList)
    print(int(float(ffmpeg.probe(appdir+"/track/164.aac")
          ["streams"][0]["duration"])*1000))
