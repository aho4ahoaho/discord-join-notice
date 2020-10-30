import discord
import time
import os
from gtts import gTTS

client = discord.Client()

if not discord.opus.is_loaded() and os.name == "posix":
    exit()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    if not os.path.isdir("voice"):
        os.mkdir("voice")
            
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!ELT") and os.path.isfile("voice/ELT.aac"):
        if (not message.author.voice) or (not message.author.voice):
            await message.channel.send("ボイスチャンネルに入っている必要があります。")
            return
        
        if not client.user in message.author.voice.channel.members:
            await message.author.voice.channel.connect(reconnect=True)
        
        voice_client = message.author.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio("voice/ELT.aac"))
    
    if message.content.startswith("!Estop"):
        if (not message.author.voice) or (not message.author.voice):
            await message.channel.send("ボイスチャンネルに入っている必要があります。")
            return

        if client.user in message.author.voice.channel.members:
            voice_client = message.author.guild.voice_client
            voice_client.stop()
            await voice_client.disconnect()

@client.event
async def on_voice_state_update(member,before,after):
    if member == client.user:
        return

    if not (after.deaf or after.mute or after.self_mute or after.afk or str(after.channel)=="None"):
        name = member.display_name
        if not os.path.isfile("voice/"+name+"mp3"):
            tts = gTTS(text=name+"さんが入室しました。",lang="ja")
            tts.save("voice/"+name+".mp3")
        
        if not client.user in member.voice.channel.members:
            await member.voice.channel.connect(reconnect=True)        
        
        voice_client = member.guild.voice_client

        if voice_client.is_playing():
            voice_client.stop()
        
        voice_client.play(discord.FFmpegPCMAudio("voice/"+name+".mp3"))
    
    if str(after.channel)=="None" and len(before.channel.members) == 1:
        await member.guild.voice_client.disconnect()


try:
    with open("token","r") as token:
        client.run(token.read())
except:
    with open("token","a") as token:
        token.write("")
    print("tokenがありません")