import discord
import pytube
from discord.ext import commands


intents = discord.Intents.all()


bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def play(ctx, query: str):

    youtube = pytube.YouTube(query)
    video = youtube.streams.first()

    audio_url = video.url
    ...

    voice_channel = ctx.message.author.voice.channel
    voice_client = await voice_channel.connect()

    player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_url))
    await voice_client.play(player)


@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.pause()


@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.resume()


bot.run('YOUR BOT TOKEN')
