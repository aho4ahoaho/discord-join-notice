import discord
import ffmpeg
import os
import random
from asyncio import sleep

appdir = os.path.dirname(os.path.abspath(__file__))

TrackList = []


class MusicPlayer:
    def __init__(self, client, guild, volume=1):
        self.client = client
        self.guild = guild
        self.volume = volume
        self.playing_track = ""
        self.queue = random.sample(TrackList, len(TrackList))
        pass

    async def connect(self, member):
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

    def play(self, sound_path):
        voice_client = self.guild.voice_client
        self.playing_track = ""
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(sound_path), volume=self.volume))

    def stop(self):
        voice_client = self.guild.voice_client
        self.playing_track = ""
        if voice_client.is_playing():
            voice_client.stop()

    def random(self):
        self.queue = random.sample(TrackList, len(TrackList))

    async def playlist(self):
        while True:
            # キューが空なら終了
            if len(self.queue) == 0:
                break

            # キューから曲を取り出す
            track = self.queue.pop()
            # パスを作る
            track_path = appdir+"/track/"+track+".aac"
            # 曲を再生する
            self.play(track_path)
            # 自分が再生した曲を覚える
            self.playing_track = track

            # 曲の長さを取得する
            track_len = float(ffmpeg.probe(track_path)[
                "streams"][0]["duration"])
            # 曲の長さだけスリープする
            await sleep(track_len)

            while self.playing_track == track and self.guild.voice_client.is_playing():
                await sleep(3)

            # 現在再生している曲が自分だったら次の曲を流す
            if self.playing_track != track:
                break


def scan_file():
    filelist = list()
    for p in os.scandir(appdir+"/track"):
        if p.is_file():
            filelist.append(".".join(p.name.split(".")[:-1]))
    TrackList.clear()
    TrackList.extend(filelist)
    return filelist


if __name__ == "__main__":
    scan_file()
    print(TrackList)
    print(int(float(ffmpeg.probe(appdir+"/track/164.aac")
          ["streams"][0]["duration"])*1000))
