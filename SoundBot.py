import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch"
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

queues = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def get_audio(query):
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        info = data["entries"][0] if "entries" in data else data
        return info

async def play_next(guild):
    if queues[guild]:
        info = queues[guild].pop(0)
        source = discord.FFmpegPCMAudio(info["url"], **FFMPEG_OPTIONS)
        guild.voice_client.play(
            source,
            after=lambda _: asyncio.run_coroutine_threadsafe(
                play_next(guild), bot.loop
            )
        )

@bot.tree.command(name="play", description="Play a song from YouTube")
@app_commands.describe(query="Song name or URL")
async def play(interaction: discord.Interaction, query: str):
    if not interaction.user.voice:
        return await interaction.response.send_message(
            "❌ You must be in a voice channel.", ephemeral=True
        )

    await interaction.response.defer()

    voice = interaction.guild.voice_client
    if not voice:
        voice = await interaction.user.voice.channel.connect()

    info = await get_audio(query)
    queues.setdefault(interaction.guild, []).append(info)

    if not voice.is_playing():
        await play_next(interaction.guild)

    embed = discord.Embed(
        title="🎵 Added to Queue",
        description=info["title"],
        color=discord.Color.blue()
    )
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="pause", description="Pause playback")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸ Paused")

@bot.tree.command(name="resume", description="Resume playback")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Resumed")

@bot.tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ Skipped")

@bot.tree.command(name="stop", description="Stop and disconnect")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        queues.pop(interaction.guild, None)
        await vc.disconnect()
        await interaction.response.send_message("⏹ Disconnected")

bot.run("YOUR_BOT_TOKEN")



bot.run('YOUR BOT TOKEN')
