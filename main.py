import discord
from discord.ext import commands
from discord import app_commands
import os
import random
from jokes import jokes
import requests
from dotenv import load_dotenv
from essay import essay_text

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member intents
logo_url = "https://avatars.githubusercontent.com/u/11970540?s=200&v=4"

bot = commands.Bot(command_prefix="!", intents=intents)

AUTHORIZED_USER_ID = [
    801475805402103859,  # Me
    221812910668775425,  # Ethan
    722854408182038683,  # Blake
    1015468364421939201, # Aaron
]

class ConfirmView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, role: discord.Role):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.role = role
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()

@bot.tree.command(name="clear_channel", description="Clear all messages in a specified channel")
async def clear_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    # Check if the user is authorized
    if interaction.user.id not in AUTHORIZED_USER_ID:
        embed = discord.Embed(
            title="Unauthorized Action",
            description="You do not have permission to run this command.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Ensure the bot has permission to manage messages in the channel
    if not channel.permissions_for(interaction.guild.me).manage_messages:
        embed = discord.Embed(
            title="Missing Permissions",
            description=f"I don't have permission to manage messages in {channel.mention}. Please make sure I have **Manage Messages** permission.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Proceed with the confirmation process
    view = ConfirmView(interaction, channel)
    embed = discord.Embed(
        title="Confirmation",
        description=f"Are you sure you want to delete all messages in {channel.mention}?",
        color=discord.Color.yellow()
    )
    embed.set_thumbnail(url=logo_url)

    # Send the initial prompt (this is the part that should stay visible)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Wait for the confirmation response
    await view.wait()

    # After waiting for the response, we need to handle the confirmation
    if view.value is None:
        embed = discord.Embed(
            title="Action Timed Out",
            description="You took too long to respond. The operation has been cancelled.",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    elif view.value:
        # If the user confirmed, delete all messages in the channel
        deleted = await channel.purge()

        embed = discord.Embed(
            title="Channel Cleared",
            description=f"Successfully deleted {len(deleted)} messages in {channel.mention}.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="Action Cancelled",
            description="The operation has been cancelled.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="remove_role", description="Remove a specified role from everyone in the server")
async def remove_role(interaction: discord.Interaction, role: discord.Role):
    success = False
    failed_members = []
    webhook_url = os.getenv('WEBHOOK_URL')
    
    webhook_embed = discord.Embed(
        title="Role Removal Command Executed",
        color=discord.Color.blue()
    )
    webhook_embed.add_field(name="User", value=interaction.user.name, inline=True)
    webhook_embed.add_field(name="User ID", value=interaction.user.id, inline=True)
    webhook_embed.add_field(name="Role", value=role.name, inline=True)
    webhook_embed.set_thumbnail(url=logo_url)

    if interaction.user.id not in AUTHORIZED_USER_ID:
        embed = discord.Embed(
            title="Unauthorized Action",
            description="You do not have permission to run this command.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        webhook_embed.add_field(name="Success", value="No (Unauthorized)", inline=True)
        requests.post(webhook_url, json={"embeds": [webhook_embed.to_dict()]})
        return

    guild = interaction.guild
    if not guild.me.guild_permissions.manage_roles:
        embed = discord.Embed(
            title="Missing Permissions",
            description="I don't have the required permissions to manage roles. Please grant me the **Manage Roles** permission.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        webhook_embed.add_field(name="Success", value="No (Missing Permissions)", inline=True)
        requests.post(webhook_url, json={"embeds": [webhook_embed.to_dict()]})
        return

    if guild.me.top_role.position <= role.position:
        embed = discord.Embed(
            title="Role Hierarchy Error",
            description="I cannot remove this role because it is higher than my highest role. Please ensure my role is above the role you want to manage.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        webhook_embed.add_field(name="Success", value="No (Role Hierarchy Error)", inline=True)
        requests.post(webhook_url, json={"embeds": [webhook_embed.to_dict()]})
        return

    # **Defer the interaction to prevent the "This interaction failed" message**
    await interaction.response.defer(ephemeral=True)

    # **Send the confirmation message**
    view = ConfirmView(interaction, role)
    embed = discord.Embed(
        title="Confirmation",
        description=f"Are you sure you want to remove the role '{role.name}' from all members who have it?",
        color=discord.Color.yellow()
    )
    embed.set_thumbnail(url=logo_url)
    await interaction.followup.send(embed=embed, view=view)

    await view.wait()

    if view.value is None:
        await interaction.edit_original_response(content="Timed out. The role removal has been cancelled.", view=None)

        webhook_embed.add_field(name="Success", value="No (Timed out)", inline=True)
        requests.post(webhook_url, json={"embeds": [webhook_embed.to_dict()]})
        return
    elif view.value:
        success = True
        for member in guild.members:
            if role in member.roles:
                try:
                    await member.remove_roles(role)
                except discord.Forbidden:
                    failed_members.append(member.name)
                    success = False

        if success:
            embed = discord.Embed(
                title="Success",
                description=f"Successfully removed the role {role.name} from all members who had it.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="Partial Success",
                description=f"Removed the role {role.name} from some members, but failed for: {', '.join(failed_members)}.",
                color=discord.Color.orange()
            )

        embed.set_thumbnail(url=logo_url)
        await interaction.edit_original_response(embed=embed, view=None)

        webhook_embed.add_field(name="Success", value="Yes" if success else "No", inline=True)
        if failed_members:
            webhook_embed.add_field(name="Failed Members", value=", ".join(failed_members), inline=False)
        requests.post(webhook_url, json={"embeds": [webhook_embed.to_dict()]})
    else:
        embed = discord.Embed(
            title="Role Removal Cancelled",
            description="The role removal process has been cancelled.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.edit_original_response(embed=embed, view=None)
        
        webhook_embed.add_field(name="Success", value="No (Cancelled)", inline=True)
        requests.post(webhook_url, json={"embeds": [webhook_embed.to_dict()]})


@bot.tree.command(name="bad_joke", description="Get a specified quantity of random bad jokes")
async def bad_joke(interaction: discord.Interaction, quantity: int):
    if quantity < 1:
        embed = discord.Embed(
            title="Invalid Number",
            description="Please enter a number greater than 0.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    selected_jokes = random.sample(jokes, min(quantity, len(jokes)))

    embed = discord.Embed(
        title="Bad Jokes",
        description="\n\n".join(selected_jokes),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=logo_url)
    await interaction.response.send_message(embed=embed)

@bot.command(name='what_is_real?')
async def what_is_real(ctx):
    print("Someone found me")
    await ctx.send(str(essay_text))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()
    print('Bot is synced')

bot.run(os.getenv('SECRET_DISCORD_KEY'))
