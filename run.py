import discord
import os
import sys
import ffmpeg
from gen_voice import gen_voice
import re

intents=discord.Intents.all()
intents.typing = False
client = discord.Client(intents=intents)
appdir = os.path.dirname(os.path.abspath(__file__))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    #voiceフォルダ生成
    if not os.path.isdir(appdir+"/voice"):
        os.mkdir(appdir+"/voice")
            
@client.event
async def on_message(message):
    #自分を無視
    if message.author == client.user:
        return

    if message.content.startswith("!tracklist"):
        tracklist = list()
        for f in os.listdir(appdir+"/voice/"):
            if f.endswith(".aac"):
                tracklist.append(f[:-4])
        await message.channel.send(content="\n".join(tracklist),delete_after=20)

    if message.content.startswith("!"):
        if os.path.isfile(appdir+"/voice/"+str(message.content).replace("!","")+".aac"):
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
            voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(appdir+"/voice/"+str(message.content).replace("!","")+".aac"),volume=0.5))
            return
    
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
        #配信停止は弾く
        try:
            if before.selfstream:
                return
        except:
            pass
            
        #同じVoiceChannelに居ない場合は接続
        if not client.user in member.voice.channel.members:
            await member.voice.channel.connect(reconnect=True)

        #キャッシュになければ音声生成
        if not os.path.isfile(appdir+"/voice/"+str(member.display_name).replace("/","")+"_join.mp3"):
            tts_gen(str(member.display_name).replace("/",""))
        
        #音声再生
        voice_client = member.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio(appdir+"/voice/"+str(member.display_name).replace("/","")+"_join.mp3"))


    #最後の一人が居なくなったら切断
    if str(after.channel)=="None" and len(before.channel.members) == 1 :
        await member.guild.voice_client.disconnect()
        return
    
    #キャッシュ容量が100MBを超えた場合削除
    if get_dir_size(appdir+"/voice")>100:
        aac=re.compile(r".*.aac")
        with os.scandir(appdir+"/voice") as File:
            for entry in File:
                if aac.match(entry.name):
                    os.remove(entry.name)
        
#voiceディレクトリのサイズチェック
def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
    return int(total/1024/1204)

#ボイスの生成
def tts_gen(name):
    text=name+"さんが入室しました。"

    with open(appdir+"/voice/temp.wav","wb") as voice:
        voice.write(gen_voice(text))
    stream = ffmpeg.input(appdir+"/voice/temp.wav")
    stream = ffmpeg.output(stream,appdir+"/voice/"+name+"_join.mp3")
    ffmpeg.run(stream)
    

#トークン読み込み、なければ引数、駄目なら警告を返して終了
try:
    with open(appdir+"/token","r") as token:
        client.run(token.read())
except:
    try:
        client.run(sys.argv[1])
    except:
        with open(appdir+"/token","a") as token:
            token.write("")
        print("tokenがありません")
