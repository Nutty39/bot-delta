import discord
from discord.ext import commands
import asyncio
import json
import os
import random
from datetime import datetime
from collections import defaultdict

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= DATA =================
levels = {}
economy = defaultdict(lambda: {"balance": 100, "daily": None})
keys = {}

@bot.event
async def on_ready():
    print(f"✅ Delta Executor Bot → Connecté et corrigé")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

# ================= HELP =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA", color=0x00ffff)
    embed.add_field(name="📢 Delta", value="`!annonce` `!key` `!redeem` `!tokeninfo` `!status` `!delta` `!scripts` `!changelog`", inline=False)
    embed.add_field(name="🧹 Clear", value="`!clear <nombre>` `!clearall <nombre>`", inline=False)
    embed.add_field(name="🔥 Nuke", value="`!nuke` `!nukeall`", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level`", inline=False)
    embed.add_field(name="💰 Économie", value="`!balance` `!daily`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!mute`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

# ================= DELTA COMMANDS =================
@bot.command()
@commands.has_permissions(administrator=True)
async def annonce(ctx, *, message):
    embed = discord.Embed(title="📢 Delta Executor", description=message, color=0x00ffff)
    await ctx.send("@everyone", embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def key(ctx, member: discord.Member = None):
    member = member or ctx.author
    key = "DELTA-" + "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=20))
    keys[key] = member.id
    await ctx.send(f"{member.mention} Clé générée :\n`{key}`")

@bot.command()
async def redeem(ctx, key: str):
    if key in keys:
        role = discord.utils.get(ctx.guild.roles, name="Delta Client")
        if role:
            await ctx.author.add_roles(role)
        await ctx.send("✅ Clé validée ! Tu es maintenant **Delta Client**.")
        del keys[key]
    else:
        await ctx.send("❌ Clé invalide.")

@bot.command()
async def tokeninfo(ctx, *, token: str = None):
    if not token:
        await ctx.send("**Utilisation :** `!tokeninfo MT...`")
        return
    await ctx.send("🔍 Vérification du token...\n✅ Token semble **valide** (simulation).")

@bot.command()
async def status(ctx):
    embed = discord.Embed(title="Delta Executor Status", color=0x00ff00)
    embed.add_field(name="Version", value="1.2", inline=True)
    embed.add_field(name="Statut", value="Undetected", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def delta(ctx):
    embed = discord.Embed(title="Delta Executor PC", color=0x00ffff)
    embed.add_field(name="Statut", value="✅ Undetected 2026", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def scripts(ctx):
    await ctx.send("**Scripts disponibles :** Infinite Yield, Fly Script, God Mode, Aimbot, ESP, Speed, Auto Farm...")

# ================= BASIQUES =================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages supprimés.", delete_after=4)

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    new = await ctx.channel.clone()
    await ctx.channel.delete()
    await new.send("**Salon nuké par Delta Executor** 🔥")

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(embed=discord.Embed(title=f"Avatar de {member}", color=0x00ffff).set_image(url=member.display_avatar.url))

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("❌ TOKEN MANQUANT DANS LES SECRETS")
else:
    bot.run(token)
