from gen_voice import gen_voice
from musicplayer import MusicPlayer, scan_file, TrackList
from romantokana import englishkana
import ffmpeg
import os
from discord import Client, Message, Member, VoiceState, Intents
from dotenv import load_dotenv
load_dotenv()


intents = Intents.all()
intents.typing = False
client = Client(intents=intents)
appdir = os.path.dirname(os.path.abspath(__file__))
musicPlayers: dict[str, MusicPlayer] = {}


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

    #!で始まらないものはコマンドではないので無視
    if not message.content.startswith("!"):
        return

    #!helpでヘルプ表示
    if message.content.startswith("!help"):
        context = ["!tracklist : 再生可能な曲を表示", "!random : ランダムなプレイリストを生成", "!skip : プレイリストの次の曲を再生",
                   "!stop : 再生中の曲を停止", "!disconnect : VCから切断", "!pronunciation <読み> : 名前の読みを修正する", "!nowplaying : 現在再生中の曲を表示",
                   "!reload : 音楽フォルダを強制リロード", "!help : このヘルプを表示", "!previous : プレイリストの前の曲を再生", "!resume : 一時停止した曲を再生","!queue : プレイリストを表示"]
        await message.channel.send(content="\n".join(sorted(context)), delete_after=120)
        return

    # tracklistを表示
    if message.content.startswith("!tracklist"):
        context = format_track(TrackList)
        context[-1] += "\n\n{}曲".format(len(TrackList))
        for c in context:
            await message.channel.send(content=c, delete_after=40)
        return
    # 音楽フォルダを強制リロード
    if message.content.startswith("!reload"):
        scan_file()
        return

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

    # これより下はVCに利用者が接続していないと利用不能
    if not message.author.voice:
        return

    #!stopで音声停止
    if message.content.startswith("!stop"):
        # サーバーに対応したプレイヤーがあれば停止
        if message.guild.id in musicPlayers.keys():
            musicPlayers[message.guild.id].stop()
        return

    #!disconnectで音声停止と切断
    if message.content.startswith("!disconnect"):
        # サーバーに対応したプレイヤーがあれば切断して削除
        if message.guild.id in musicPlayers.keys():
            await musicPlayers[message.guild.id].disconnect()
            musicPlayers.pop(message.guild.id)
        return

    #!nowplayingで現在再生中の曲を表示
    if message.content.startswith("!nowplaying"):
        # サーバーに対応したプレイヤーがあれば再生中の曲を表示
        if message.guild.id in musicPlayers.keys():
            context = musicPlayers[message.guild.id].now_playing()
            if context is None:
                context = "再生中の曲はありません"
            else:
                context = "再生中の曲は\nです。"+context
            await message.channel.send(content=context, delete_after=20)

    # これより下はVCに本botが接続している場合のみ利用可能
    if message.guild.id in musicPlayers.keys():
        #!skipで次の曲
        if message.content.startswith("!skip"):
            # 次の曲を再生
            await musicPlayers[message.guild.id].playlist()

        #!resumeで再開
        if message.content.startswith("!resume"):
            # 再生
            await musicPlayers[message.guild.id].resume()

        #!previousで前の曲に戻る
        if message.content.startswith("!previous"):
            # 再生
            await musicPlayers[message.guild.id].previous()

        #!queueでキューを表示
        if message.content.startswith("!queue"):
            # キューを取得
            queue = musicPlayers[message.guild.id].queue
            index = musicPlayers[message.guild.id].index
            context = format_track(queue[index:])
            for c in context:
            # キューを表示
                await message.channel.send(content=c, delete_after=20)

    if message.content.startswith("!random"):
        # サーバーに対応したプレイヤーがあればランダム再生
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

    #!<曲名>で任意の曲を再生
    trackname = str(message.content).replace("!", "")
    if trackname in TrackList:
        if not message.guild.id in musicPlayers.keys():
            musicPlayers[message.guild.id] = MusicPlayer(
                client, message.guild, 0.25)
        # ボイスチャンネルに接続
        await musicPlayers[message.guild.id].connect(message.author)
        # 指定のファイルを再生
        musicPlayers[message.guild.id].play(appdir+"/track/"+trackname+".aac")


def format_track(track_list: list[str]) -> list[str]:
    context_lines = []
    # 2列で表示
    for i in range(0, len(track_list), 2):
        t1 = track_list[i][:20] #+("i"*max(0, 20-len(track_list[i])))
        if i+1 < len(track_list):
            t2 = track_list[i+1][:20]
            context_lines.append("{}\t\t{}\n".format(t1, t2))
        else:
            context_lines.append("{}\t\t\n".format(t1))

    # 2000文字で分割
    context = []
    index = 0
    count = 0
    for i in range(len(context_lines)):
        count += len(context_lines[i])
        if count > 2000:
            context.append("".join(context_lines[index:i]))
            index = i
            count = len(context_lines[i])
    context.append("".join(context_lines[index:]))
    return context


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

    # VoiceChannelへの入室していない、または人数が1人の場合は無視
    if member.voice is None or len(after.channel.members) <= 1:
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
def get_dir_size(path: str = '.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
    return int(total/1024/1204)


# OPENAIのAPIキーをチェック
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    from get_phonetic import getPhonetic
else:
    print("GPT less mode")

# ボイスの生成


def tts_gen(name: str, pronunciation: str = ""):
    yomi = name.strip()
    if (pronunciation != ""):
        yomi = pronunciation
    else:
        if openai_key:
            yomi = getPhonetic(yomi)
        else:
            yomi = englishkana(yomi)
    text = yomi+"さんが入室しました。"
    with open(appdir+"/voice/temp.wav", "wb") as voice:
        voice.write(gen_voice(text))
    stream = ffmpeg.input(appdir+"/voice/temp.wav")
    stream = ffmpeg.output(stream, appdir+"/voice/"+name+"_join.mp3")
    ffmpeg.run(stream, overwrite_output=True)


# トークン読み込み、なければ引数、駄目なら警告を返して終了
discord_key = os.getenv("DISCORD_API_KEY")
if discord_key:
    client.run(discord_key)
