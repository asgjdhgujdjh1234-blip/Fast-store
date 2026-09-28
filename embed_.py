import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput

TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


class ConfirmView(View):
    def __init__(self, room_id, message, image_url=None):
        super().__init__(timeout=300)
        self.room_id = room_id
        self.message = message
        self.image_url = image_url

    @discord.ui.button(label="Send", style=discord.ButtonStyle.green)
    async def send_button(self, interaction: discord.Interaction, button: Button):
        try:
            channel = interaction.guild.get_channel(int(self.room_id))

            if channel is None:
                try:
                    channel = await bot.fetch_channel(int(self.room_id))
                except:
                    await interaction.response.send_message(
                        "The room ID is invalid or I cannot access that room.",
                        ephemeral=True
                    )
                    return

            embed = discord.Embed(
                description=self.message,
                color=discord.Color.green()
            )

            if self.image_url:
                embed.set_image(url=self.image_url)

            await channel.send(embed=embed)

            await interaction.response.edit_message(
                content=f"Sent successfully to <#{channel.id}>.",
                embed=None,
                view=None
            )

        except Exception as e:
            await interaction.response.send_message(
                f"Failed to send the message.\n`{e}`",
                ephemeral=True
            )

    @discord.ui.button(label="Unsend", style=discord.ButtonStyle.red)
    async def unsend_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(
            content="The message has been cancelled.",
            embed=None,
            view=None
        )


class SendEmbedModal(Modal, title="Send an Embed"):
    room_id = TextInput(
        label="Room ID",
        placeholder="Enter the channel ID",
        required=True,
        max_length=30
    )

    message = TextInput(
        label="The Message",
        placeholder="Enter the message",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            int(self.room_id.value)
        except ValueError:
            await interaction.response.send_message(
                "The Room ID must be a number.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Confirm Message",
            description=self.message.value,
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=ConfirmView(self.room_id.value, self.message.value),
            ephemeral=True
        )


class PhotoMessageModal(Modal, title="Send with a Photo"):
    room_id = TextInput(
        label="Room ID",
        placeholder="Enter the channel ID",
        required=True,
        max_length=30
    )

    message = TextInput(
        label="The Message",
        placeholder="Enter the message",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            int(self.room_id.value)
        except ValueError:
            await interaction.response.send_message(
                "The Room ID must be a number.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Now send the image you want to use.",
            ephemeral=True
        )

        def check(msg):
            return (
                msg.author.id == interaction.user.id
                and msg.channel.id == interaction.channel.id
                and len(msg.attachments) > 0
            )

        try:
            msg = await bot.wait_for(
                "message",
                check=check,
                timeout=300
            )
        except TimeoutError:
            await interaction.followup.send(
                "You took too long to send the image.",
                ephemeral=True
            )
            return

        image = msg.attachments[0]

        if not image.content_type or not image.content_type.startswith("image/"):
            await interaction.followup.send(
                "The file you sent is not an image.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Confirm Message",
            description=self.message.value,
            color=discord.Color.blurple()
        )

        embed.set_image(url=image.url)

        await interaction.followup.send(
            embed=embed,
            view=ConfirmView(
                self.room_id.value,
                self.message.value,
                image.url
            ),
            ephemeral=True
        )


class SendView(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Send a Embed",
        style=discord.ButtonStyle.green
    )
    async def embed_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await interaction.response.send_modal(SendEmbedModal())

    @discord.ui.button(
        label="Send with a Photo",
        style=discord.ButtonStyle.blurple
    )
    async def photo_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await interaction.response.send_modal(PhotoMessageModal())


@bot.command()
async def send(ctx):
    embed = discord.Embed(
        title="Send Message",
        description="Choose how you want to send the message.",
        color=discord.Color.blurple()
    )

    await ctx.send(
        embed=embed,
        view=SendView()
    )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")


bot.run(TOKEN)