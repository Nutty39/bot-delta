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
afk_users = {}

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
    print(f"Bot lancé → {bot.user} - Chargé à fond")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tout niquer"))
    auto_cleanup.start()

@bot.event
async def on_member_join(member):
    welcome = discord.utils.get(member.guild.text_channels, name="bienvenue")
    if welcome:
        await welcome.send(f"{member.mention} a rejoint.")

    now = datetime.utcnow()
    join_times[member.guild.id].append(now)
    join_times[member.guild.id] = [t for t in join_times[member.guild.id] if now - t < timedelta(seconds=10)]

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

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.message_id) in reaction_roles:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(reaction_roles[str(payload.message_id)])
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.add_roles(role)

# ================= NOUVELLE COMMANDE !FONCTION =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES FONCTIONS DU BOT", description="Voici la liste complète :", color=0xff0000)
    
    embed.add_field(name="🔧 Général", value="`!ping` `!help` `!fonction`", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="💰 Économie", value="`!balance` `!daily` `!pay` `!shop` `!buyrole`", inline=False)
    embed.add_field(name="🎉 Fun", value="`!giveaway` `!fake_nitro` `!ticket` `!afk` `!reactionrole`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!unban` `!warn` `!slowmode` `!lock` `!unlock` `!setclean`", inline=False)
    embed.add_field(name="💥 Destruction", value="`!nuke` `!nukeall` `!webhookspam` `!raidmode`", inline=False)
    embed.add_field(name="🔍 Autres", value="`!tokeninfo`", inline=False)
    
    embed.set_footer(text="Tape !fonction pour revoir cette liste")
    await ctx.send(embed=embed)

# ================= AUTRES COMMANDES (résumé) =================
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong → {round(bot.latency * 1000)}ms")

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

@bot.command()
async def memberinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    embed = discord.Embed(title=str(member), color=0xff0000)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Level", value=levels.get(str(member.id), {"level":1})["level"])
    embed.add_field(name="Argent", value=economy[str(member.id)]["balance"])
    embed.add_field(name="Rôles", value=", ".join(roles)[:500] or "Aucun")
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(embed=discord.Embed(title=f"Avatar {member}", color=0xff0000).set_image(url=member.display_avatar.url))

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
        msg += f"{i}. {u.mention if u else uid} → Level {d['level']}\n"
    await ctx.send(msg)

@bot.command()
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"{member.mention} → **{economy[str(member.id)]['balance']} coins**")

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
async def fake_nitro(ctx):
    code = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=19))
    await ctx.send(f"https://discord.gift/{code}")

@bot.command()
@commands.has_permissions(administrator=True)
async def webhookspam(ctx, amount: int = 10, *, text="SPAM"):
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
    for ch in ctx.guild.channels[:]:
        try:
            await ch.delete()
        except:
            pass
    await ctx.guild.create_text_channel("nuke-fini")

@bot.command()
@commands.has_permissions(administrator=True)
async def setclean(ctx, channel: discord.TextChannel, seconds: int):
    config[str(channel.id)] = {"delete_after": seconds}
    save_config()
    await ctx.send(f"Auto clean activé ({seconds}s) sur {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} ban.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} unbanni.")

@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, duration: int, *, prize):
    embed = discord.Embed(title="🎉 GIVEAWAY", description=prize, color=0x00ff00)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(duration)
    msg = await ctx.channel.fetch_message(msg.id)
    users = [u async for u in msg.reactions[0].users() if not u.bot]
    if users:
        await ctx.send(f"**Gagnant :** {random.choice(users).mention} → {prize}")
    else:
        await ctx.send("Pas de gagnant.")

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("TOKEN MANQUANT")
else:
    bot.run(token)
