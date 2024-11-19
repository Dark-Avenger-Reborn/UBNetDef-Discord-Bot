import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
intents.members = True  # Necessary to manage members and roles
logo_url = "https://avatars.githubusercontent.com/u/11970540?s=200&v=4"

# Create a bot instance with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Hardcoded User ID for the admin that can execute the command
AUTHORIZED_USER_ID = [
    801475805402103859,  #Me
    221812910668775425,  #Ethan
    722854408182038683,  #Blake
    ]

@bot.tree.command(name="remove_role", description="Remove a specified role from everyone in the server")
async def remove_role(interaction: discord.Interaction, role: discord.Role):
    # Replace with your authorization logic
    if interaction.user.id not in AUTHORIZED_USER_ID:
        embed = discord.Embed(
            title="Unauthorized Action",
            description="You do not have permission to run this command.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Get the guild (server)
    guild = interaction.guild

    # Ensure the bot has permission to manage roles
    if not guild.me.guild_permissions.manage_roles:
        embed = discord.Embed(
            title="Missing Permissions",
            description="I don't have the required permissions to manage roles in this server. Please grant me the **Manage Roles** permission.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        embed.add_field(name="How to Fix", value="1. Go to Server Settings > Roles.\n2. Make sure my role has **Manage Roles** permission.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Ensure the bot's role is high enough to remove the role
    if guild.me.top_role.position <= role.position:
        embed = discord.Embed(
            title="Role Hierarchy Error",
            description="I cannot remove this role because it is higher than my highest role. Please ensure my role is above the role you want me to manage.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        embed.add_field(name="How to Fix", value="1. Go to Server Settings > Roles.\n2. Move my role higher than the role you want to manage.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Loop through all members and remove the role
    for member in guild.members:
        if role in member.roles:
            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                embed = discord.Embed(
                    title="Permission Denied",
                    description=f"Could not remove the role from {member.name} due to missing permissions. I may not have sufficient permissions for that user.",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=logo_url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                continue

    embed = discord.Embed(
        title="Success",
        description=f"Successfully removed the role {role.name} from all members who had it.",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=logo_url)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()  # Sync the slash commands with Discord


bot.run(env.SECRET_DISCORD_KEY)