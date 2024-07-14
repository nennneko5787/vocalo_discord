import asyncio
import copy
import json
import os
import random
from datetime import datetime

import discord
from discord.app_commands import CommandTree
from discord.ext import tasks
from yt_dlp import YoutubeDL


from keep_alive import keep_alive

if os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv()

client: discord.Client = discord.Client(intents=discord.Intents.all())
tree: CommandTree = CommandTree(client)

statusMessage: str = ""


@client.event
async def on_ready():
    print(client.user, "としてログインしました")
    await loadVideos()
    print("ran `await loadVideos()`")
    await tree.sync()
    print("ran `await tree.sync()`")
    presence.start()
    print("play")
    guild: discord.Guild = client.get_guild(1124309483703763025)
    voice_client: discord.VoiceClient = guild.voice_client
    if voice_client:
        await voice_client.disconnect(force=True)
    await play()


@tasks.loop(seconds=20)
async def presence():
    await client.change_presence(activity=discord.Game(statusMessage))


videos = []
queue: asyncio.Queue = asyncio.Queue()


async def loadVideos():
    global videos
    with open("songs.txt", "r") as f:
        videos = json.load(f)
    return


def getcolor(title: str, description: str) -> discord.Colour:
    text = f"{title}\t{description}".lower()
    if "初音" in text or "hatsune" in text or "hatune" in text:
        return discord.Colour.from_str("#c3e5e7")
    elif "鏡音" in text or "kagamine" in text:
        return discord.Colour.from_str("#fcf5a7")
    elif "巡音" in text or "megurine" in text:
        return discord.Colour.from_str("#ebd3cf")
    elif "kaito" in text:
        return discord.Colour.from_str("#413a87")
    elif "meiko" in text:
        return discord.Colour.from_str("#cb213c")
    elif "ia" in text:
        return discord.Colour.from_str("#c0c0c0")
    elif "gumi" in text:
        return discord.Colour.from_str("#32cd32")
    elif "可不" in text or "kafu" in text:
        return discord.Colour.from_str("#d8bfd8")
    else:
        return None


playing = False


async def after_playback():
    global playing
    playing = False


async def playSongs():
    global queue
    global playing
    guild: discord.Guild = client.get_guild(1124309483703763025)
    voice_client: discord.VoiceProtocol = guild.voice_client
    video = None
    dic = None
    ydl = YoutubeDL()
    while True:
        if not voice_client:
            channel: discord.VoiceChannel = client.get_channel(
                1261937281548161094
            )
            await channel.connect()
        if not video:
            video = await queue.get()
        if not dic:
            dic = await asyncio.to_thread(
                lambda: ydl.extract_info(
                    video.get("webpage_url", ""), download=False
                )
            )
        url = dic.get("url")
        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        source = await discord.FFmpegOpusAudio.from_probe(
            url, **FFMPEG_OPTIONS
        )
        await asyncio.to_thread(
            voice_client.play,
            source,
            after=lambda e: after_playback(),
        )

        title = video.get("title")
        webpage_url = video.get("webpage_url")
        thumbnail = video.get("thumbnail")
        description = video.get("description")
        embed = (
            discord.Embed(
                title=title,
                url=webpage_url,
                timestamp=datetime.now(),
                color=getcolor(title, description),
            )
            .set_author(name="再生中")
            .set_image(url=thumbnail)
        )
        await client.get_channel(1261937281548161094).send(embed=embed)

        if queue.qsize() <= 0:
            videoList = copy.deepcopy(videos)
            random.shuffle(videoList)
            for video in videoList:
                await queue.put(
                    {
                        "webpage_url": video.get("webpage_url"),
                        "url": video.get("url"),
                        "title": video.get("title"),
                        "id": video.get("id"),
                        "thumbnail": video.get("thumbnail"),
                        "description": video.get("description"),
                    }
                )

        video = await queue.get()
        ydl = YoutubeDL()
        dic = await asyncio.to_thread(
            lambda: ydl.extract_info(
                video.get("webpage_url", ""), download=False
            )
        )
        while playing:
            asyncio.sleep(0)


@tree.command(name="play", description="再生が効かなくなってしまったとき用")
async def playCommand(interaction: discord.Interaction):
    voice_client: discord.VoiceClient = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect(force=True)
    await play()


async def play():
    global videos
    global queue

    guild: discord.Guild = client.get_guild(1124309483703763025)

    if not guild.voice_client:
        channel: discord.VoiceChannel = client.get_channel(1261937281548161094)
        await channel.connect()
        videoList = copy.deepcopy(videos)
        random.shuffle(videoList)
        for video in videoList:
            await queue.put(
                {
                    "webpage_url": video.get("webpage_url"),
                    "url": video.get("url"),
                    "title": video.get("title"),
                    "id": video.get("id"),
                    "thumbnail": video.get("thumbnail"),
                    "description": video.get("description"),
                }
            )
        await playSongs()


keep_alive()

TOKEN = os.getenv("discord")
client.run(TOKEN)
