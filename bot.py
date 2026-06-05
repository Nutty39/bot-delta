import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import random
from datetime import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= CONFIG & XP =================
levels = {}
tickets = {}

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"Bot lancé → {bot.user} - Tout est niqué")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="optimiser ta merde"))
    auto_cleanup.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # XP System
    author_id = str(message.author.id)
    if author_id not in levels:
        levels[author_id] = {"xp": 0, "level": 1}
    levels[author_id]["xp"] += random.randint(5, 20)

    if levels[author_id]["xp"] >= levels[author_id]["level"] * 150:
        levels[author_id]["level"] += 1
        levels[author_id]["xp"] = 0
        await message.channel.send(f"🎉 {message.author.mention} passe au **Level {levels[author_id]['level']}** !")

    # Auto clean
    channel_id = str(message.channel.id)
    rules = config.get(channel_id, {})
    deleted = False

    if rules.get("delete_after"):
        await asyncio.sleep(rules["delete_after"])
        try:
            await message.delete()
            deleted = True
        except:
            pass

    if deleted and discord.utils.get(message.guild.text_channels, name="logs-bot"):
        await discord.utils.get(message.guild.text_channels, name="logs-bot").send(f"Supprimé dans {message.channel.mention}")

    await bot.process_commands(message)

# ================= COMMANDES =================
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong → {round(bot.latency * 1000)}ms")

@bot.command()
async def memberinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    embed = discord.Embed(title=f"Infos complètes → {member}", color=0xff0000)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Pseudo", value=str(member))
    embed.add_field(name="Surnom", value=member.nick or "Aucun")
    embed.add_field(name="Rejoint le", value=member.joined_at.strftime("%d/%m/%Y %H:%M") if member.joined_at else "Inconnu")
    embed.add_field(name="Créé le", value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Rôles", value=", ".join(roles) if roles else "Aucun", inline=False)
    embed.add_field(name="Level", value=levels.get(str(member.id), {"level": 1})["level"])
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"Avatar de {member}", color=0xff0000)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = levels.get(str(member.id), {"xp": 0, "level": 1})
    await ctx.send(f"{member.mention} → **Level {data['level']}** | XP: {data['xp']}")

# ================= GIVEAWAY =================
@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx, duration: int, *, prize):
    embed = discord.Embed(title="🎉 GIVEAWAY 🎉", description=f"**Prix :** {prize}\n**Durée :** {duration} secondes", color=0x00ff00)
    embed.set_footer(text="Réagis avec 🎉 pour participer !")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(duration)
    msg = await ctx.channel.fetch_message(msg.id)
    reaction = discord.utils.get(msg.reactions, emoji="🎉")
    users = [user async for user in reaction.users() if not user.bot]
    if users:
        winner = random.choice(users)
        await ctx.send(f"🎉 **Gagnant :** {winner.mention} → **{prize}** !")
    else:
        await ctx.send("Personne n'a participé...")

# ================= TICKET =================
@bot.command()
async def ticket(ctx):
    category = discord.utils.get(ctx.guild.categories, name="Tickets")
    if not category:
        category = await ctx.guild.create_category("Tickets")
    ticket_channel = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", category=category)
    await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
    await ticket_channel.set_permissions(ctx.guild.default_role, read_messages=False)
    await ticket_channel.send(f"{ctx.author.mention} bienvenue dans ton ticket. Un admin va arriver.")
    await ctx.send(f"Ticket créé → {ticket_channel.mention}")

# ================= MUSIQUE (simple) =================
@bot.command()
@commands.has_permissions(administrator=True)  # ou retire cette ligne si tu veux que tout le monde l'utilise
async def play(ctx, url: str):
    if not ctx.author.voice:
        await ctx.send("Rejoins un vocal d'abord fils de pute")
        return
    channel = ctx.author.voice.channel
    voice = await channel.connect()
    await ctx.send(f"Je joue : {url} (version basique, peut bugger)")
    # Note : Pour une vraie musique, il faut yt-dlp + FFmpeg (compliqué sur Railway)

# ================= NUKE =================
@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    new_channel = await channel.clone()
    await channel.delete()
    await new_channel.send("**Salon nuke effectué avec succès.**")
    await ctx.send("Nuke terminé.")

# ================= AUTRES =================
@bot.command()
@commands.has_permissions(administrator=True)
async def setclean(ctx, channel: discord.TextChannel, seconds: int):
    channel_id = str(channel.id)
    if channel_id not in config:
        config[channel_id] = {}
    config[channel_id]["delete_after"] = seconds
    save_config(config)
    await ctx.send(f"Nettoyage auto activé sur {channel.mention} ({seconds}s)")

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} s'est fait ban.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} unbanni.")

# ================= LANCEMENT =================
token = os.getenv("TOKEN")
if not token:
    print("ERREUR : TOKEN manquant dans les Variables")
else:
    bot.run(token)
