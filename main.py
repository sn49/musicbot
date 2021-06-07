from ntpath import realpath
import discord
from discord.ext import commands, tasks
from discord.utils import get
import youtube_dl
import asyncio
import random

bot = commands.Bot(command_prefix="m!")

tokenfile = open("token.txt", "r")
token = tokenfile.read()

playList = []
playingIndex = None


@bot.command()
async def shuffle(ctx):
    global playList

    random.shuffle(playList)


@bot.command()
async def connect(ctx):
    ch = ctx.author.voice.channel
    await ch.connect()


async def realPlay(index):
    global playingIndex
    global urlList

    mpeg_opt = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    playingIndex = int(index)

    voice = bot.voice_clients[0]
    voice.play(discord.FFmpegPCMAudio(playList[int(index) - 1][1], **mpeg_opt))


@bot.command()
async def playcheck(ctx):
    global playingIndex
    voice = bot.voice_clients[0]

    if not voice.is_playing() and not voice.is_paused():
        playingIndex=None
        await ctx.send(f"재생하고 있는 곡이 없음")
    else:
        await ctx.send(f"{playingIndex} : {playList[int(playingIndex) - 1][0]} 재생중")

    


@bot.command()
async def play(ctx, index):
    await realPlay(index)


@bot.command()
async def add(ctx, url):
    global urlList
    global titleList

    opt = {"format": "bestaudio"}

    tempUrl = []
    tempTitle = []
    with youtube_dl.YoutubeDL(opt) as ydl:
        yurl = None
        info = ydl.extract_info(url, download=False)

        if "entries" in info.keys():
            for i in info["entries"]:
                tempUrl.append(i["url"])
                tempTitle.append(i["title"])
        else:
            tempUrl.append(info["url"])
            tempTitle.append(info["title"])

    index = 0

    for i in tempUrl:
        if not [tempTitle[index], i] in playList:
            playList.append([tempTitle[index], i])
            print(len(playList))
        index += 1


@bot.command()
async def reset(ctx):
    global playList

    playList.clear()


@bot.command()
async def check(ctx):
    global playList
    sendtext = "```"

    index = 1

    for i in playList:
        sendtext += f"{index} : {i[0]}\n"

        if index % 20 == 0:
            sendtext += "```"
            await ctx.send(sendtext)
            sendtext = "```"

        index += 1

    sendtext += "```"
    await ctx.send(sendtext)


@bot.command()
async def delete(ctx, index):
    global playList
    global playingIndex

    del playList[int(index) - 1]

    if playingIndex > int(index):
        playingIndex -= 1


@bot.command()
async def autoplay(ctx):
    global playingIndex
    global playList
    voice = bot.voice_clients[0]

    while True:
        if not voice.is_playing() and not voice.is_paused():
            if playingIndex == len(playList) or playingIndex == None:
                await realPlay(1)
            else:
                await realPlay(playingIndex + 1)

        await asyncio.sleep(3)


@bot.command()
async def leave(ctx):
    await bot.voice_clients[0].disconnect()


@bot.command()
async def pause(ctx):
    await bot.voice_clients[0].pause()


@bot.command()
async def resume(ctx):
    await bot.voice_clients[0].resume()


bot.run(token)
