import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= CONFIG =================
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
    print(f"Bot lancé → {bot.user} prêt à tout casser")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="optimiser ton serveur"))
    auto_cleanup.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    channel_id = str(message.channel.id)
    rules = config.get(channel_id, {})

    deleted = False
    content = message.content.lower()

    # Règles de suppression par salon
    if rules:
        if rules.get("delete_after"):
            await asyncio.sleep(rules["delete_after"])
            try:
                await message.delete()
                deleted = True
            except:
                pass

        if rules.get("keywords") and any(kw.lower() in content for kw in rules["keywords"]):
            await message.delete()
            deleted = True

        if rules.get("max_length") and len(message.content) > rules["max_length"]:
            await message.delete()
            deleted = True

        if rules.get("no_links") and ("http" in content or "discord.gg" in content):
            await message.delete()
            deleted = True

        if rules.get("no_images") and message.attachments:
            await message.delete()
            deleted = True

    # Anti-spam global
    if len(message.content) > 800 or (message.mentions and len(message.mentions) > 5):
        await message.delete()
        deleted = True

    if deleted:
        log_channel = discord.utils.get(message.guild.text_channels, name="logs-bot")
        if log_channel:
            await log_channel.send(f"**Supprimé** | {message.channel.mention} | {message.author} : {message.content[:100]}")

    await bot.process_commands(message)

# ================= NETTOYAGE AUTO TOUS LES 30 MIN =================
@tasks.loop(minutes=30)
async def auto_cleanup():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            rules = config.get(str(channel.id), {})
            if rules.get("delete_after"):
                try:
                    async for msg in channel.history(limit=100):
                        if (datetime.utcnow() - msg.created_at).total_seconds() > rules["delete_after"] + 300:
                            await msg.delete()
                except:
                    pass

# ================= COMMANDES =================
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} a été ban.")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.kick(reason=reason)
    await ctx.send(f"{member} a été kick.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} a été unban.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages virés.", delete_after=3)

@bot.command()
@commands.has_permissions(administrator=True)
async def setclean(ctx, channel: discord.TextChannel, seconds: int):
    channel_id = str(channel.id)
    if channel_id not in config:
        config[channel_id] = {}
    config[channel_id]["delete_after"] = seconds
    save_config(config)
    await ctx.send(f"✅ Nettoyage auto activé sur {channel.mention} après **{seconds}** secondes.")

@bot.command()
@commands.has_permissions(administrator=True)
async def addkeyword(ctx, channel: discord.TextChannel, *, keyword):
    channel_id = str(channel.id)
    if channel_id not in config:
        config[channel_id] = {"keywords": []}
    config[channel_id].setdefault("keywords", []).append(keyword)
    save_config(config)
    await ctx.send(f"✅ Mot '{keyword}' interdit dans {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def noclean(ctx, channel: discord.TextChannel):
    if str(channel.id) in config:
        del config[str(channel.id)]
        save_config(config)
        await ctx.send(f"✅ Nettoyage désactivé sur {channel.mention}")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong → {round(bot.latency * 1000)}ms")

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"Avatar de {member}", color=0xff0000)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"Info sur {member}", color=0xff0000)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Pseudo", value=member.name, inline=True)
    embed.add_field(name="Surnom", value=member.nick or "Aucun", inline=True)
    embed.add_field(name="Créé le", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
    embed.add_field(name="Rejoint le", value=member.joined_at.strftime("%d/%m/%Y %H:%M") if member.joined_at else "Inconnu", inline=True)
    embed.add_field(name="Rôles", value=len(member.roles)-1, inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def memberinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    embed = discord.Embed(title=f"Infos complètes {member}", color=0xff0000)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Pseudo", value=str(member))
    embed.add_field(name="Surnom", value=member.nick or "Aucun")
    embed.add_field(name="Bot ?", value="Oui" if member.bot else "Non")
    embed.add_field(name="Créé", value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Rejoint", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "Inconnu")
    embed.add_field(name="Rôles", value=", ".join(roles) if roles else "Aucun", inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# ================= LANCEMENT =================
TOKEN = os.getenv("MTUxMjQzNzI3NTExODUzODgzMg.GDtjz_.tn3uXBzelf46E-a3KOCL67JTlI2nYNpGVx6Yg0")
if not TOKEN:
    print("ERREUR : TOKEN manquant dans les Variables")
else:
    bot.run(TOKEN)
