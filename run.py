import discord
from discord.ext import tasks
import os
import sys
import ffmpeg
from gen_voice import gen_voice
import random
from musicplayer import MusicPlayer, scan_file, TrackList

intents = discord.Intents.all()
intents.typing = False
client = discord.Client(intents=intents)
appdir = os.path.dirname(os.path.abspath(__file__))
musicPlayers = {}


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # voiceフォルダ生成
    os.makedirs(appdir+"/voice", exist_ok=True)
    os.makedirs(appdir+"/track", exist_ok=True)
    scan_file()


@client.event
async def on_message(message):
    # 自分を無視
    if message.author == client.user:
        return

    if not message.content.startswith("!"):
        return

    if message.content.startswith("!tracklist"):
        await message.channel.send(content="\n".join(sorted(TrackList))+"\n\n{}曲".format(len(TrackList)), delete_after=40)
        return

    if message.content.startswith("!random"):
        if not message.author.voice:
            return

        # サーバーに対応したプレイヤーが無ければ生成
        if not message.guild.id in musicPlayers.keys():
            musicPlayers[message.guild.id] = MusicPlayer(client, message.guild)
        else:
            musicPlayers[message.guild.id].random()
        # ボイスチャンネルに接続
        await musicPlayers[message.guild.id].connect(message.author)
        # 指定のファイルを再生
        await musicPlayers[message.guild.id].playlist()
        return
    
    if message.content.startswith("!reload"):
        if not message.author.voice:
            return
        scan_file()
        return

    #!stopで音声停止
    if message.content.startswith("!stop"):
        if not message.author.voice:
            return

        # サーバーに対応したプレイヤーがあれば停止
        if message.guild.id in musicPlayers.keys():
            musicPlayers[message.guild.id].stop()
        return

    #!disconnectで音声停止と切断
    if message.content.startswith("!disconnect"):
        if not message.author.voice:
            return

        # サーバーに対応したプレイヤーが無ければ切断して削除
        if message.guild.id in musicPlayers.keys():
            await musicPlayers[message.guild.id].disconnect()
            musicPlayers.pop(message.guild.id)
        return

    #!skipで次の曲
    if message.content.startswith("!skip"):
        if not message.author.voice:
            return
        # サーバーに対応したプレイヤーが無ければ生成
        if not message.guild.id in musicPlayers.keys():
            return
        # 次の曲を再生
        await musicPlayers[message.guild.id].playlist()

    #!helpでヘルプ表示
    if message.content.startswith("!help"):
        context = ["!tracklist : 再生可能な曲を表示", "!random : ランダムなプレイリストを生成", "!skip : プレイリストの次の曲を再生",
                   "!stop : 再生中の曲を停止", "!disconnect : VCから切断"]
        await message.channel.send(content="\n".join(context), delete_after=120)
        return

    trackname = str(message.content).replace("!", "")
    if trackname in TrackList:
        # サーバーに対応したプレイヤーが無ければ生成
        if not message.guild.id in musicPlayers.keys():
            musicPlayers[message.guild.id] = MusicPlayer(client, message.guild)
        # ボイスチャンネルに接続
        await musicPlayers[message.guild.id].connect(message.author)
        # 指定のファイルを再生
        musicPlayers[message.guild.id].play(appdir+"/track/"+trackname+".aac")


@client.event
async def on_voice_state_update(member, before, after):
    # 自分を無視
    if member == client.user:
        return

    # 接続したら分岐
    if not (after.deaf or after.mute or after.self_mute or after.self_deaf or after.self_stream or after.afk or str(after.channel) == "None" or len(after.channel.members) == 1):
        # 配信停止は弾く
        try:
            if before.selfstream:
                return
        except:
            pass

        # VoiceChannelへの入室必須
        if not member.voice:
            return

        sound_path = appdir+"/voice/" + \
            str(member.display_name).replace("/", "")+"_join.mp3"
        # キャッシュになければ音声生成
        if not os.path.isfile(sound_path):
            tts_gen(str(member.display_name).replace("/", ""))
        # サーバーに対応したプレイヤーが無ければ生成
        if not member.guild.id in musicPlayers.keys():
            musicPlayers[member.guild.id] = MusicPlayer(client, member.guild)
        # ボイスチャンネルに接続
        await musicPlayers[member.guild.id].connect(member)
        # 音声を再生
        musicPlayers[member.guild.id].play(sound_path)

    # 最後の一人が居なくなったら切断
    if str(after.channel) == "None" and len(before.channel.members) == 1:
        if member.guild.id in musicPlayers.keys():
            musicPlayers[member.guild.id].stop()
            musicPlayers.pop(member.guild.id)
        return

    # キャッシュ容量が100MBを超えた場合削除
    if get_dir_size(appdir+"/voice") > 100:
        with os.scandir(appdir+"/voice") as File:
            for entry in File:
                if entry.name[-4:] != ".aac":
                    os.remove(appdir+"/voice/"+entry.name)


# ディレクトリのサイズチェック


def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
    return int(total/1024/1204)

# ボイスの生成


def tts_gen(name):
    text = name+"さんが入室しました。"

    with open(appdir+"/voice/temp.wav", "wb") as voice:
        voice.write(gen_voice(text))
    stream = ffmpeg.input(appdir+"/voice/temp.wav")
    stream = ffmpeg.output(stream, appdir+"/voice/"+name+"_join.mp3")
    ffmpeg.run(stream)


# トークン読み込み、なければ引数、駄目なら警告を返して終了
try:
    with open(appdir+"/token", "r") as token:
        client.run(token.read())
except:
    try:
        client.run(sys.argv[1])
    except:
        with open(appdir+"/token", "a") as token:
            token.write("")
        print("tokenがありません")
