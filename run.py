import discord
import time
import os
import sys
from gtts import gTTS

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    #voiceフォルダ生成
    if not os.path.isdir("voice"):
        os.mkdir("voice")
            
@client.event
async def on_message(message):
    #自分を無視
    if message.author == client.user:
        return

    #!ELTに反応し、尚且ELT.aacが用意されいる場合のみ反応
    if message.content.startswith("!ELT") and os.path.isfile("voice/ELT.aac"):
        #VoiceChannelへの入室必須
        if not message.author.voice:
            return
        #投稿者と同じVoiceChannelに居ない場合は接続
        if not client.user in message.author.voice.channel.members:
            await message.author.voice.channel.connect(reconnect=True)
        #再生中の音源があれば止めてplay
        voice_client = message.author.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio("voice/ELT.aac"))
    
    #!Etopで音声停止と切断
    if message.content.startswith("!Estop"):
        if not message.author.voice:
            return

        if client.user in message.author.voice.channel.members:
            voice_client = message.author.guild.voice_client
            voice_client.stop()
            await voice_client.disconnect()

@client.event
async def on_voice_state_update(member,before,after):
    #自分を無視
    if member == client.user:
        return
    
    #接続したら分岐
    if not (after.deaf or after.mute or after.self_mute or after.self_deaf or after.self_stream or after.afk or str(after.channel)=="None" or len(after.channel.members) == 1):
        #同じVoiceChannelに居ない場合は接続
        if not client.user in member.voice.channel.members:
            await member.voice.channel.connect(reconnect=True)

        #キャッシュになければ音声生成
        if not os.path.isfile("voice/"+member.display_name+"_join.mp3"):
            tts_gen(member.display_name)
        
        #音声再生
        voice_client = member.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio("voice/"+member.display_name+"_join.mp3"))


    #最後の一人が居なくなったら切断
    if str(after.channel)=="None" and len(before.channel.members) == 1 :
        await member.guild.voice_client.disconnect()
        return
    
    #キャッシュ容量が100MBを超えた場合削除
    if get_dir_size("voice")>100:
        with os.scandir("voice") as File:
            for entry in File:
                if entry.name != "ELT.aac":
                    os.remove(entry.name)
        
#voiceディレクトリのサイズチェック
def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
    return int(total/1024/1204)

#gTTsの生成、失敗した場合は再帰処理
def tts_gen(name):
    try:
        tts = gTTS(text=name+"さんが入室しました。",lang="ja")
        tts.save("voice/"+name+"_join.mp3")
    except:
        tts_gen(name)

#token読み込み、なければ空ファイル生成と警告
try:
    with open("token","r") as token:
        client.run(token.read())
except:
    try:
        client.run(sys.argv[1])
    except:
        with open("token","a") as token:
            token.write("")
        print("tokenがありません")