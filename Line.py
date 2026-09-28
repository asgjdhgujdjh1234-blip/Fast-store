import discord
from discord.ext import commands
import json
import os

TOKEN = ""
DATA_FILE = "line_rooms.json"
IMAGE_FILE = "fastline3.png"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_rooms():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_rooms(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


line_rooms = load_rooms()


class RoomModal(discord.ui.Modal, title="إضافة روم Line"):
    room_id = discord.ui.TextInput(
        label="Room ID",
        placeholder="اكتب ID الروم هنا",
        required=True,
        min_length=17,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        room_id = self.room_id.value.strip()

        if not room_id.isdigit():
            await interaction.response.send_message(
                "ID الروم غير صحيح.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(int(room_id))

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "ما لقيت روم كتابي بهذا الـ ID.",
                ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)
        channel_id = str(channel.id)

        if guild_id not in line_rooms:
            line_rooms[guild_id] = []

        if channel_id in line_rooms[guild_id]:
            await interaction.response.send_message(
                f"الروم {channel.mention} موجود بالقائمة بالفعل.",
                ephemeral=True
            )
            return

        line_rooms[guild_id].append(channel_id)
        save_rooms(line_rooms)

        await interaction.response.send_message(
            f"تمت إضافة {channel.mention} إلى قائمة الـ Line.",
            ephemeral=True
        )


class LineView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="إضافة روم",
        style=discord.ButtonStyle.primary,
        custom_id="fastline_add_room"
    )
    async def add_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RoomModal())


@bot.command()
@commands.has_permissions(administrator=True)
async def line(ctx):
    guild_id = str(ctx.guild.id)
    rooms = line_rooms.get(guild_id, [])

    valid_rooms = []

    for room_id in rooms:
        channel = ctx.guild.get_channel(int(room_id))

        if isinstance(channel, discord.TextChannel):
            valid_rooms.append(channel)

    line_rooms[guild_id] = [str(channel.id) for channel in valid_rooms]
    save_rooms(line_rooms)

    if not valid_rooms:
        room_text = "ما فيه رومات بالمكان"
    else:
        room_text = "\n".join(
            f"{index}. {channel.mention}"
            for index, channel in enumerate(valid_rooms, 1)
        )

    embed = discord.Embed(
        title="Fast Line",
        description=f"**الرومات الحالية:**\n{room_text}",
        color=discord.Color.purple()
    )

    await ctx.send(
        embed=embed,
        view=LineView()
    )


@line.error
async def line_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need Administrator permission to use this command.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild:
        guild_id = str(message.guild.id)
        rooms = line_rooms.get(guild_id, [])

        if str(message.channel.id) in rooms:
            if os.path.exists(IMAGE_FILE):
                await message.channel.send(
                    file=discord.File(IMAGE_FILE)
                )

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    print("Fast Line is ready.")


bot.run(TOKEN)
