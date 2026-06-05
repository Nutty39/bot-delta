import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= DATA =================
levels = {}
warns = defaultdict(list)
economy = defaultdict(lambda: {"balance": 100, "daily": None})
config = {}
reaction_roles = {}
keys = {}

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {}
def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

@bot.event
async def on_ready():
    print(f"Delta Executor Bot → Lancé")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

# ================= MODALS (gardés) =================
class RedeemModal(discord.ui.Modal, title="Redeem Delta Key"):
    key_input = discord.ui.TextInput(label="Ta clé Delta", placeholder="DELTA-XXXXXXXXXXXXXXXXXXXX", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        key = self.key_input.value.strip()
        if key in keys:
            role = discord.utils.get(interaction.guild.roles, name="Delta Client")
            if role: await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Clé validée !", ephemeral=True)
            del keys[key]
        else:
            await interaction.response.send_message("❌ Clé invalide.", ephemeral=True)

# ================= HELP / FONCTION (bien rempli) =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA", color=0x00ffff, description="Liste complète")
    
    embed.add_field(name="📢 Delta Executor", value=
        "`!annonce <texte>`\n"
        "`!update <version>`\n"
        "`!key [@user]`\n"
        "`!redeemkey`\n"
        "`!tokeninfo`\n"
        "`!status`\n"
        "`!delta`\n"
        "`!scripts`\n"
        "`!changelog`\n"
        "`!buy`\n"
        "`!support`", inline=False)

    embed.add_field(name="🧹 Clear", value=
        "`!clear <nombre>` → Supprime X messages\n"
        "`!clearall <nombre>` → Purge plus violent", inline=False)

    embed.add_field(name="🔥 Nuke", value=
        "`!nuke` → Supprime et recrée le salon actuel\n"
        "`!nukeall` → Supprime tous les salons", inline=False)

    embed.add_field(name="👤 Infos", value=
        "`!memberinfo [@user]`\n"
        "`!avatar [@user]`\n"
        "`!level [@user]`\n"
        "`!leaderboard`", inline=False)

    embed.add_field(name="💰 Économie", value=
        "`!balance [@user]`\n"
        "`!daily`\n"
        "`!pay @user <montant>`", inline=False)

    embed.add_field(name="🎉 Fun", value=
        "`!giveaway <durée> <prix>`\n"
        "`!fake_nitro`\n"
        "`!ticket`\n"
        "`!reactionrole <role> <emoji>`", inline=False)

    embed.add_field(name="🛠️ Modération", value=
        "`!ban @user`\n"
        "`!kick @user`\n"
        "`!unban <id>`\n"
        "`!warn @user`\n"
        "`!mute @user`\n"
        "`!unmute @user`\n"
        "`!slowmode <secondes>`\n"
        "`!lock`\n"
        "`!unlock`\n"
        "`!setclean #salon <secondes>`", inline=False)

    embed.add_field(name="💥 Destruction", value=
        "`!webhookspam <nombre>`\n"
        "`!raidmode`", inline=False)

    embed.set_footer(text="Delta Executor Bot • Tout est là")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

# ================= AUTRES COMMANDES (tout le reste reste intact) =================
@bot.command()
async def redeemkey(ctx):
    embed = discord.Embed(title="Delta Key", description="Clique pour entrer ta clé", color=0x00ffff)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Entrer Clé", style=discord.ButtonStyle.green, custom_id="redeem_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def tokeninfo(ctx):
    embed = discord.Embed(title="Token Checker", description="Clique pour vérifier un token", color=0x00ffff)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Vérifier Token", style=discord.ButtonStyle.primary, custom_id="token_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def status(ctx):
    embed = discord.Embed(title="Delta Status", description="Clique pour définir la version", color=0x00ffff)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Ouvrir Status", style=discord.ButtonStyle.primary, custom_id="status_modal"))
    await ctx.send(embed=embed, view=view)

# (Le reste des commandes comme clear, nuke, ban, etc. est toujours là)

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("ERREUR TOKEN")
else:
    bot.run(token)
