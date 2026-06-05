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

levels = {}
warns = defaultdict(list)
economy = defaultdict(lambda: {"balance": 100, "daily": None})
config = {}
join_times = defaultdict(list)
reaction_roles = {}

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
    print(f"Bot lancé → {bot.user} - Tout est chargé à fond")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tout niquer"))
    auto_cleanup.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    aid = str(message.author.id)
    if aid not in levels:
        levels[aid] = {"xp": 0, "level": 1}
    levels[aid]["xp"] += random.randint(10, 40)
    if levels[aid]["xp"] >= levels[aid]["level"] * 100:
        levels[aid]["level"] += 1
        levels[aid]["xp"] = 0
        await message.channel.send(f"🎉 {message.author.mention} level **{levels[aid]['level']}** !")

    economy[aid]["balance"] += random.randint(2, 8)

    if str(message.channel.id) in config and config[str(message.channel.id)].get("delete_after"):
        await asyncio.sleep(config[str(message.channel.id)]["delete_after"])
        try:
            await message.delete()
        except:
            pass

    await bot.process_commands(message)

# ================= HELP DÉTAILLÉ =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 TOUT CE QUE LE BOT SAIT FAIRE", description="Commandes complètes :", color=0xff0000)
    
    embed.add_field(name="🧹 Clear", value="`!clear nombre` → Supprime X messages\n`!clearall nombre` → Purge plus violent", inline=False)
    embed.add_field(name="🔥 Nuke", value="`!nuke` → Supprime et recrée le salon actuel", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="💰 Économie", value="`!balance` `!daily` `!pay`", inline=False)
    embed.add_field(name="🎉 Fun", value="`!giveaway` `!fake_nitro` `!ticket` `!reactionrole`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!unban` `!warn` `!mute` `!unmute` `!slowmode` `!lock` `!unlock` `!setclean`", inline=False)
    embed.add_field(name="💥 Destruction", value="`!nukeall` `!webhookspam` `!raidmode`", inline=False)
    embed.add_field(name="🔍 Divers", value="`!tokeninfo TOKEN` `!ping` `!fonction`", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def fonction(ctx):
    await ctx.invoke(bot.get_command('help'))

# ================= NUKE FIXÉ =================
@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    try:
        new_channel = await channel.clone(reason="Nuke command")
        await channel.delete(reason="Nuke command")
        await new_channel.send("**Salon nuke effectué avec succès.** 🔥")
        await ctx.send(f"Salon {channel.name} nuké et recréé.", delete_after=5)
    except Exception as e:
        await ctx.send(f"Erreur pendant le nuke : {e}")

# ================= CLEAR =================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    if amount > 100: amount = 100
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages supprimés.", delete_after=4)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearall(ctx, amount: int = 50):
    if amount > 200: amount = 200
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages virés.", delete_after=4)

# ================= MODÉRATION =================
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} a été ban.")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune"):
    await member.kick(reason=reason)
    await ctx.send(f"{member} a été kick.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"{user} a été unbanni.")
    except:
        await ctx.send("ID invalide.")

@bot.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, minutes: int = 10):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for ch in ctx.guild.channels:
            await ch.set_permissions(role, send_messages=False, speak=False)
    await member.add_roles(role)
    await ctx.send(f"{member} muté pour {minutes} minutes.")
    await asyncio.sleep(minutes * 60)
    await member.remove_roles(role)

@bot.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role:
        await member.remove_roles(role)
        await ctx.send(f"{member} unmute.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Slowmode mis à {seconds} secondes.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Salon verrouillé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Salon déverrouillé.")

# ================= AUTRES =================
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong → {round(bot.latency * 1000)}ms")

@bot.command()
async def fake_nitro(ctx):
    code = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=19))
    await ctx.send(f"https://discord.gift/{code}")

@bot.command()
@commands.has_permissions(administrator=True)
async def webhookspam(ctx, amount: int = 10, *, text="SPAM DE MERDE"):
    for _ in range(amount):
        try:
            wh = await ctx.channel.create_webhook(name="spam")
            await wh.send(text * 5)
            await wh.delete()
        except:
            pass
    await ctx.send("Webhook spam terminé.")

@bot.command()
@commands.has_permissions(administrator=True)
async def nukeall(ctx):
    for ch in list(ctx.guild.channels):
        try:
            await ch.delete()
        except:
            pass
    await ctx.guild.create_text_channel("nuke-termine")

@bot.command()
@commands.has_permissions(administrator=True)
async def setclean(ctx, channel: discord.TextChannel, seconds: int):
    config[str(channel.id)] = {"delete_after": seconds}
    save_config()
    await ctx.send(f"Auto clean {seconds}s activé sur {channel.mention}")

@bot.command()
async def tokeninfo(ctx, token: str):
    if len(token) < 50:
        await ctx.send("Token trop court.")
        return
    try:
        headers = {"Authorization": token}
        async with bot.http._HTTPClient__session.get("https://discord.com/api/v9/users/@me", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(f"✅ Token valide → {data.get('username')}#{data.get('discriminator')}")
            else:
                await ctx.send("❌ Token invalide.")
    except:
        await ctx.send("Erreur pendant la vérification.")

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("ERREUR : TOKEN MANQUANT DANS SECRETS")
else:
    bot.run(token)
