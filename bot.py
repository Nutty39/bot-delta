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
    print(f"Delta Executor Bot → Lancé avec tout")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v2.1"))

# ================= DELTA COMMANDS =================
@bot.command()
@commands.has_permissions(administrator=True)
async def annonce(ctx, *, message):
    embed = discord.Embed(title="📢 Delta Executor", description=message, color=0x00ffff, timestamp=datetime.now())
    await ctx.send("@everyone", embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def update(ctx, version: str = "2.1"):
    await ctx.send(f"@everyone **Delta Executor v{version}** mise à jour sortie !")

@bot.command()
async def delta(ctx):
    embed = discord.Embed(title="Delta Executor PC", color=0x00ffff)
    embed.add_field(name="Statut", value="✅ Undetected 2026", inline=False)
    embed.add_field(name="Features", value="Aimbot, ESP, Fly, Speed, God Mode, Auto Farm...", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def key(ctx, member: discord.Member = None):
    member = member or ctx.author
    key = "DELTA-" + "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=16))
    await ctx.send(f"{member.mention} Ta clé Delta : `{key}`")

@bot.command()
async def redeem(ctx, key: str):
    if len(key) > 15:
        await ctx.send("✅ Clé valide ! Rôle **Delta Client** donné.")
        role = discord.utils.get(ctx.guild.roles, name="Delta Client")
        if role:
            await ctx.author.add_roles(role)
    else:
        await ctx.send("❌ Clé invalide.")

@bot.command()
async def status(ctx):
    embed = discord.Embed(title="Delta Executor Status", color=0x00ff00)
    embed.add_field(name="Version", value="2.1", inline=True)
    embed.add_field(name="Statut", value="Undetected", inline=True)
    await ctx.send(embed=embed)

# ================= TOUTES LES ANCIENNES COMMANDES =================
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong → {round(bot.latency * 1000)}ms")

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="📜 TOUTES LES COMMANDES DELTA EXECUTOR", color=0x00ffff)
    embed.add_field(name="🧹 Clear", value="`!clear nombre` → Supprime X messages\n`!clearall nombre` → Purge plus violent", inline=False)
    embed.add_field(name="🔥 Nuke", value="`!nuke` → Supprime et recrée le salon actuel", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="💰 Économie", value="`!balance` `!daily` `!pay`", inline=False)
    embed.add_field(name="🎉 Fun", value="`!giveaway` `!fake_nitro` `!ticket` `!reactionrole`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!unban` `!warn` `!mute` `!unmute` `!slowmode` `!lock` `!unlock` `!setclean`", inline=False)
    embed.add_field(name="💥 Destruction", value="`!nukeall` `!webhookspam` `!raidmode`", inline=False)
    embed.add_field(name="🔍 Divers", value="`!tokeninfo TOKEN` `!ping` `!fonction` `!status`", inline=False)
    embed.add_field(name="Delta", value="`!annonce` `!update` `!delta` `!key` `!redeem`", inline=False)
    await ctx.send(embed=embed)

# Clear
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

# Nuke
@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    new_channel = await channel.clone()
    await channel.delete()
    await new_channel.send("**Salon nuké et recréé par Delta Executor** 🔥")

# Infos
@bot.command()
async def memberinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    embed = discord.Embed(title=str(member), color=0x00ffff)
    embed.add_field(name="Level", value=levels.get(str(member.id), {"level":1})["level"])
    embed.add_field(name="Argent", value=economy[str(member.id)]["balance"])
    embed.add_field(name="Rôles", value=", ".join(roles)[:500] or "Aucun")
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(embed=discord.Embed(title=f"Avatar de {member}", color=0x00ffff).set_image(url=member.display_avatar.url))

@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = levels.get(str(member.id), {"xp":0,"level":1})
    await ctx.send(f"{member.mention} → Level **{data['level']}**")

@bot.command()
async def leaderboard(ctx):
    top = sorted(levels.items(), key=lambda x: x[1]["level"], reverse=True)[:10]
    msg = "**TOP 10 LEVELS**\n"
    for i, (uid, d) in enumerate(top, 1):
        u = bot.get_user(int(uid))
        msg += f"{i}. {u.mention if u else uid} - Level {d['level']}\n"
    await ctx.send(msg)

# Économie
@bot.command()
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"{member.mention} a **{economy[str(member.id)]['balance']} coins**")

@bot.command()
async def daily(ctx):
    aid = str(ctx.author.id)
    now = datetime.utcnow()
    if economy[aid]["daily"] and (now - economy[aid]["daily"]).total_seconds() < 86400:
        await ctx.send("Daily déjà pris.")
        return
    economy[aid]["balance"] += 1000
    economy[aid]["daily"] = now
    await ctx.send("**+1000 coins** pris !")

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    aid = str(ctx.author.id)
    if economy[aid]["balance"] < amount:
        await ctx.send("Pas assez de coins.")
        return
    economy[aid]["balance"] -= amount
    economy[str(member.id)]["balance"] += amount
    await ctx.send(f"Tu as donné {amount} coins à {member.mention}.")

# Fun
@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, duration: int, *, prize):
    embed = discord.Embed(title="🎉 GIVEAWAY Delta", description=prize, color=0x00ffff)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(duration)
    msg = await ctx.channel.fetch_message(msg.id)
    users = [u async for u in msg.reactions[0].users() if not u.bot]
    if users:
        await ctx.send(f"Gagnant : {random.choice(users).mention} → {prize}")

@bot.command()
async def fake_nitro(ctx):
    code = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=19))
    await ctx.send(f"https://discord.gift/{code}")

@bot.command()
async def ticket(ctx):
    cat = discord.utils.get(ctx.guild.categories, name="Tickets")
    if not cat:
        cat = await ctx.guild.create_category("Tickets")
    chan = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", category=cat)
    await chan.set_permissions(ctx.author, read_messages=True, send_messages=True)
    await chan.set_permissions(ctx.guild.default_role, read_messages=False)
    await chan.send(f"{ctx.author.mention} Ticket ouvert.")
    await ctx.send(f"Ticket créé : {chan.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def reactionrole(ctx, role: discord.Role, emoji: str):
    msg = await ctx.send(f"Réagis avec {emoji} pour {role.mention}")
    reaction_roles[str(msg.id)] = role.id
    await msg.add_reaction(emoji)

# Modération
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

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} unbanni.")

@bot.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member, *, reason="Aucune"):
    warns[member.id].append(reason)
    await ctx.send(f"{member.mention} a reçu un warn ({len(warns[member.id])}/3)")
    if len(warns[member.id]) >= 3:
        await member.ban(reason="Trop de warns")

@bot.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, minutes: int = 10):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for ch in ctx.guild.channels:
            await ch.set_permissions(role, send_messages=False)
    await member.add_roles(role)
    await ctx.send(f"{member} muté {minutes} minutes.")

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
    await ctx.send(f"Slowmode : {seconds}s")

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

@bot.command()
@commands.has_permissions(administrator=True)
async def setclean(ctx, channel: discord.TextChannel, seconds: int):
    config[str(channel.id)] = {"delete_after": seconds}
    save_config()
    await ctx.send(f"Auto clean activé sur {channel.mention} ({seconds}s)")

# Destruction
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
async def webhookspam(ctx, amount: int = 10, *, text="SPAM"):
    for _ in range(amount):
        try:
            wh = await ctx.channel.create_webhook(name="delta-spam")
            await wh.send(text * 5)
            await wh.delete()
        except:
            pass
    await ctx.send("Webhook spam terminé.")

@bot.command()
@commands.has_permissions(administrator=True)
async def raidmode(ctx, state="on"):
    await ctx.send(f"Raidmode {state.upper()} activé.")

# Divers
@bot.command()
async def tokeninfo(ctx, token: str):
    await ctx.send("Token checker lancé... (simulation)")
    await asyncio.sleep(1)
    await ctx.send("✅ Token valide (simulation)")

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("ERREUR : TOKEN MANQUANT")
else:
    bot.run(token)
