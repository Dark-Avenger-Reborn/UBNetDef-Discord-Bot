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

@bot.tree.command(name="remove_role", description="Remove a specified role from everyone in the server")
async def remove_role(interaction: discord.Interaction, role: discord.Role):
    if interaction.user.id not in AUTHORIZED_USER_ID:
        embed = discord.Embed(
            title="Unauthorized Action",
            description="You do not have permission to run this command.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    guild = interaction.guild

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

    view = ConfirmView(interaction, role)
    embed = discord.Embed(
        title="Confirmation",
        description=f"Are you sure you want to remove the role '{role.name}' from all members who have it?",
        color=discord.Color.yellow()
    )
    embed.set_thumbnail(url=logo_url)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    await view.wait()

    if view.value is None:
        await interaction.followup.send("Timed out. The role removal has been cancelled.", ephemeral=True)
    elif view.value:
        success = True
        failed_members = []
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
        await interaction.followup.send(embed=embed)
        
        # Send webhook notification
        webhook_url = "https://discord.com/api/webhooks/1308915463455244309/WgWMj1mbCFmQVNgdd8Tyd5yv0TcFTywKgHbQ3cGZzwyy4MHf5argblhck_S5Qalf1Fpr"
        webhook_embed = discord.Embed(
            title="Role Removal Command Executed",
            color=discord.Color.blue()
        )
        webhook_embed.add_field(name="User", value=interaction.user.name, inline=True)
        webhook_embed.add_field(name="User ID", value=interaction.user.id, inline=True)
        webhook_embed.add_field(name="Role", value=role.name, inline=True)
        webhook_embed.add_field(name="Success", value="Yes" if success else "No", inline=True)
        if failed_members:
            webhook_embed.add_field(name="Failed Members", value=", ".join(failed_members), inline=False)
        webhook_embed.set_thumbnail(url=logo_url)

        requests.post(webhook_url, json={"embeds": [webhook_embed.to_dict()]})

    else:
        await interaction.followup.send("Role removal cancelled.", ephemeral=True)

@bot.tree.command(name="bad_joke", description="Get a specified number of random bad jokes")
async def bad_joke(interaction: discord.Interaction, number: int):
    if number < 1:
        embed = discord.Embed(
            title="Invalid Number",
            description="Please enter a number greater than 0.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=logo_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    selected_jokes = random.sample(jokes, min(number, len(jokes)))

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

@bot.tree.command(name="incident", description="Report an incident.")
async def incident(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Incident Report: SSH Misconfiguration",
        description="Details of the observed issue and resolution steps.",
        color=discord.Color.red()
    )
    embed.add_field(
        name="Incident",
        value="RIT performed a break\n`ssh`: moving `whoami` to `whoareyou`",
        inline=False
    )
    embed.add_field(
        name="Fix",
        value="Moving `/bin/whoareyou` back to `/bin/whoami`",
        inline=False
    )
    embed.add_field(
        name="Discovery",
        value="This issue can be verified as broken by checking the scoring engine.",
        inline=False
    )
    embed.add_field(
        name="Systems Affected",
        value="`10.8.1.40`",
        inline=False
    )
    embed.set_footer(
        text="Ensure systems are secured and the scoring engine reflects the fix.",
        icon_url="https://cdn-icons-png.flaticon.com/512/847/847969.png"
    )
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()
    print('Bot is synced')

bot.run(os.getenv('SECRET_DISCORD_KEY'))
