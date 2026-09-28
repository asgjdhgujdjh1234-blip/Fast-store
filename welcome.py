import discord
from discord.ext import commands

TOKEN = ""
GUILD_ID = 1376262368236929196
CHANNEL_ID = 1552429050247520337

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return

    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        await channel.send(
            f"**Welcome To Fast Store ({member.mention})\n"
            f"Member : {member.guild.member_count}\n"
            f"Enjoy !**"
        )

bot.run(TOKEN)
