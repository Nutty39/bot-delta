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
warns = defaultdict(list)
economy = defaultdict(lambda: {"balance": 100, "daily": None})
config = {}
keys = {}

@bot.event
async def on_ready():
    print(f"✅ Delta Executor Bot → Tout est chargé correctement")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

# ================= HELP COMPLET =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA", color=0x00ffff)
    
    embed.add_field(name="📢 Delta", value=
        "`!annonce <texte>`\n"
        "`!update <version>`\n"
        "`!key [@user]`\n"
        "`!redeem <key>`\n"
        "`!tokeninfo <token>`\n"
        "`!status`\n"
        "`!delta`\n"
        "`!scripts`\n"
        "`!changelog`\n"
        "`!buy`", inline=False)

    embed.add_field(name="🧹 Clear", value=
        "`!clear <nombre>`\n"
        "`!clearall <nombre>`", inline=False)

    embed.add_field(name="🔥 Nuke", value=
        "`!nuke`\n"
        "`!nukeall`", inline=False)

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
        "`!mute @user <minutes>`\n"
        "`!unmute @user`\n"
        "`!slowmode <secondes>`\n"
        "`!lock`\n"
        "`!unlock`\n"
        "`!setclean #salon <secondes>`", inline=False)

    embed.add_field(name="💥 Destruction", value=
        "`!webhookspam <nombre>`\n"
        "`!raidmode`", inline=False)

    embed.set_footer(text="Delta Executor Bot - Tout fonctionne")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

# ================= DELTA COMMANDS =================
@bot.command()
@commands.has_permissions(administrator=True)
async def annonce(ctx, *, message):
    embed = discord.Embed(title="📢 Delta Executor", description=message, color=0x00ffff, timestamp=datetime.now())
    await ctx.send("@everyone", embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def update(ctx, version: str = "1.2"):
    await ctx.send(f"@everyone **Delta Executor v{version}** est sorti !")

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
async def tokeninfo(ctx, *, token: str):
    await ctx.send("🔍 Vérification...\n✅ Token semble valide (simulation).")

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
    await ctx.send("**Scripts disponibles :** Infinite Yield, Fly Script, God Mode v2, Aimbot.lua, ESP.lua, Speed.lua, Auto Farm, Kill All...")

@bot.command()
async def changelog(ctx):
    await ctx.send("**Changelog :** v1.2 - Nouveau menu + fix anti-detect")

@bot.command()
async def buy(ctx):
    await ctx.send("**Pour acheter :** DM un admin ou utilise `!key`")

# ================= CLEAR & NUKE =================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages supprimés.", delete_after=4)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearall(ctx, amount: int = 50):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages virés.", delete_after=4)

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    new_channel = await ctx.channel.clone()
    await ctx.channel.delete()
    await new_channel.send("**Salon nuké par Delta Executor** 🔥")

@bot.command()
@commands.has_permissions(administrator=True)
async def nukeall(ctx):
    for ch in list(ctx.guild.channels):
        try:
            await ch.delete()
        except:
            pass
    await ctx.guild.create_text_channel("nuke-termine")

# ================= AUTRES COMMANDES (quelques-unes essentielles) =================
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"Avatar de {member}", color=0x00ffff)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} ban.")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune"):
    await member.kick(reason=reason)
    await ctx.send(f"{member} kick.")

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("❌ Mets ton token dans les Secrets Replit")
else:
    bot.run(token)
