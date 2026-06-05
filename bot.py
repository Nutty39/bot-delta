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
    print(f"Bot lancé → {bot.user} - Tout est chargé")
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

# ================= !HELP DÉTAILLÉ =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 AIDE COMPLÈTE DU BOT", description="Toutes les commandes avec explication :", color=0xff0000)
    
    embed.add_field(name="🔧 Basiques", value=
        "`!ping` → Vérifie si le bot est vivant\n"
        "`!fonction` → Liste rapide des commandes\n"
        "`!help` → Cette aide détaillée", inline=False)
    
    embed.add_field(name="👤 Infos Joueur", value=
        "`!memberinfo [@user]` → Toutes les infos du membre\n"
        "`!avatar [@user]` → Montre l'avatar\n"
        "`!level [@user]` → Ton niveau XP\n"
        "`!leaderboard` → Top 10 levels", inline=False)
    
    embed.add_field(name="💰 Économie", value=
        "`!balance [@user]` → Voir ton argent\n"
        "`!daily` → Prends 1000 coins par jour\n"
        "`!pay @user montant` → Donne de l'argent", inline=False)
    
    embed.add_field(name="🎉 Fun", value=
        "`!giveaway durée prix` → Ex: `!giveaway 60 Nitro`\n"
        "`!fake_nitro` → Génère un faux lien nitro\n"
        "`!ticket` → Crée un ticket privé\n"
        "`!reactionrole @role emoji` → Rôle par réaction", inline=False)
    
    embed.add_field(name="🛠️ Modération", value=
        "`!ban @user` → Ban\n"
        "`!unban ID` → Unban avec l'ID\n"
        "`!warn @user raison` → Warn (3 = ban auto)\n"
        "`!slowmode secondes` → Slowmode\n"
        "`!lock` / `!unlock` → Verrouille/déverrouille salon\n"
        "`!setclean #salon secondes` → Auto suppression", inline=False)
    
    embed.add_field(name="💥 Destruction", value=
        "`!nuke` → Recrée le salon actuel\n"
        "`!nukeall` → Supprime TOUS les salons\n"
        "`!webhookspam nombre texte` → Spam webhook\n"
        "`!raidmode` → Active le mode raid", inline=False)
    
    embed.add_field(name="🔍 Divers", value=
        "`!tokeninfo TOKEN` → Vérifie si un token est valide", inline=False)
    
    embed.set_footer(text="Fait par ton bot de merde - Tout est admin only sauf les basiques")
    await ctx.send(embed=embed)

@bot.command()
async def fonction(ctx):
    await ctx.invoke(bot.get_command('help'))

# ================= TOKENINFO FIXÉ =================
@bot.command()
async def tokeninfo(ctx, token: str):
    if len(token) < 50:
        await ctx.send("Token trop court, envoie un vrai.")
        return
    try:
        headers = {"Authorization": token}
        async with bot.http._HTTPClient__session.get("https://discord.com/api/v9/users/@me", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                await ctx.send(f"✅ **Token valide !**\nUser: {data.get('username')}#{data.get('discriminator')}\nID: {data.get('id')}")
            else:
                await ctx.send("❌ Token invalide ou expiré.")
    except:
        await ctx.send("Erreur lors de la vérification (token probablement mort).")

# ================= AUTRES COMMANDES (quelques fixes) =================
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong → {round(bot.latency * 1000)}ms")

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
    await ctx.send(embed=discord.Embed(title=f"Avatar de {member}", color=0xff0000).set_image(url=member.display_avatar.url))

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
    await ctx.send(f"Auto clean activé sur {channel.mention} ({seconds}s)")

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} a été ban.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"{user} a été unbanni.")
    except:
        await ctx.send("Impossible de trouver cet ID.")

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("ERREUR : TOKEN MANQUANT DANS SECRETS")
else:
    bot.run(token)
