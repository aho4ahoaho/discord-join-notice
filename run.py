import ffmpeg
import sys
import os
from discord import Client, Message, Member, VoiceState, Intents
from dotenv import load_dotenv
load_dotenv()

from get_phonetic import getPhonetic
from musicplayer import MusicPlayer, scan_file, TrackList
from gen_voice import gen_voice


intents = Intents.all()
intents.typing = False
client = Client(intents=intents)
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
async def on_message(message: Message):
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
            musicPlayers[message.guild.id] = MusicPlayer(
                client, message.guild, 0.25)
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
                   "!stop : 再生中の曲を停止", "!disconnect : VCから切断", "!pronunciation <読み> : 名前の読みを修正する", "!nowplaying : 現在再生中の曲を表示"]
        await message.channel.send(content="\n".join(context), delete_after=120)
        return

    #!nowplayingで現在再生中の曲を表示
    if message.content.startswith("!nowplaying"):
        # サーバーに対応したプレイヤーが無ければ切断して削除
        if message.guild.id in musicPlayers.keys():
            context = musicPlayers[message.guild.id].playing_track
            await message.channel.send(content=context, delete_after=20)

    #!pronunciationで読みの変更
    if message.content.startswith("!pronunciation"):
        if message.content[14:].strip() == "remove":
            sound_path = appdir+"/voice/" + \
                str(message.author.display_name).replace("/", "")+"_join.mp3"
            # キャッシュになければ音声生成
            if os.path.isfile(sound_path):
                os.remove(sound_path)
            return
        tts_gen(str(message.author.display_name).replace(
            "/", ""), message.content[14:46].strip())

    trackname = str(message.content).replace("!", "")
    if trackname in TrackList:
        # サーバーに対応したプレイヤーが無ければ生成
        if not message.guild.id in musicPlayers.keys():
            musicPlayers[message.guild.id] = MusicPlayer(
                client, message.guild, 0.25)
        # ボイスチャンネルに接続
        await musicPlayers[message.guild.id].connect(message.author)
        # 指定のファイルを再生
        musicPlayers[message.guild.id].play(appdir+"/track/"+trackname+".aac")


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    # 自分を無視
    if member == client.user:
        return

    # 最後の一人が居なくなったら切断
    if str(after.channel) == "None" and len(before.channel.members) == 1:
        if member.guild.id in musicPlayers.keys():
            await musicPlayers[member.guild.id].disconnect()
            musicPlayers.pop(member.guild.id)
        return

    # キャッシュ容量が100MBを超えた場合削除
    if get_dir_size(appdir+"/voice") > 100:
        with os.scandir(appdir+"/voice") as File:
            for entry in File:
                if entry.name[-4:] != ".aac":
                    os.remove(appdir+"/voice/"+entry.name)

    # VoiceChannelへの入室必須
    if not member.voice:
        return
    # beforeがミュートではないかつafterがミュートの場合はreturn
    if (not before.mute and after.mute) or (not before.self_mute and after.self_mute):
        return
    # beforeが配信がオンでafterが配信オフの場合はreturn
    if (before.self_stream != after.self_stream) or (before.self_video != after.self_video):
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
    musicPlayers[member.guild.id].play(sound_path, 1.2)
    return


# ディレクトリのサイズチェック
def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
    return int(total/1024/1204)

# ボイスの生成


def tts_gen(name, pronunciation=""):
    yomi = name
    if (pronunciation != ""):
        yomi = pronunciation
    yomi = getPhonetic(yomi.strip())
    text = yomi+"さんが入室しました。"
    with open(appdir+"/voice/temp.wav", "wb") as voice:
        voice.write(gen_voice(text))
    stream = ffmpeg.input(appdir+"/voice/temp.wav")
    stream = ffmpeg.output(stream, appdir+"/voice/"+name+"_join.mp3")
    ffmpeg.run(stream, overwrite_output=True)


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
