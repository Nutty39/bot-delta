import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime, timedelta
from collections import defaultdict
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= DATA =================
levels = defaultdict(lambda: {"xp": 0, "level": 1})
warns = defaultdict(list)
economy = defaultdict(lambda: {"balance": 100, "daily": None})
keys = {}

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Delta Executor Bot → Connecté en tant que {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    levels[message.author.id]["xp"] += random.randint(5, 15)
    if levels[message.author.id]["xp"] >= levels[message.author.id]["level"] * 100:
        levels[message.author.id]["level"] += 1
        levels[message.author.id]["xp"] = 0
        await message.channel.send(f"🎉 {message.author.mention} est passé au niveau **{levels[message.author.id]['level']}** !")
    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data and interaction.data.get("custom_id") == "redeem_modal":
        await interaction.response.send_modal(RedeemModal())

# ================= MODAL =================
class RedeemModal(discord.ui.Modal, title="Redeem Delta Key"):
    key_input = discord.ui.TextInput(label="Ta clé Delta", placeholder="DELTA-XXXXXXXXXXXXXXXXXXXX", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        key = self.key_input.value.strip()
        if key in keys:
            role = discord.utils.get(interaction.guild.roles, name="Delta Client")
            if role:
                await interaction.user.add_roles(role)
            del keys[key]
            await interaction.response.send_message("✅ Clé validée !", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Clé invalide.", ephemeral=True)

# ================= HELP =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA EXECUTOR", color=0x00ffff)
    embed.add_field(name="📢 Delta", value="`!annonce` `!key` `!redeemkey` `!status` `!delta` `!scripts` `!tokeninfo`", inline=False)
    embed.add_field(name="🧹 Clear & Nuke", value="`!clear` `!clearall` `!nuke` `!nukeall`", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="💰 Économie", value="`!balance` `!daily` `!pay`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!warn` `!mute` `!unmute` `!slowmode` `!lock` `!unlock`", inline=False)
    embed.add_field(name="🎵 Music", value="`!play <lien youtube/spotify>`", inline=False)
    embed.set_footer(text="Delta Executor v1.2")
    await ctx.send(embed=embed)

# ================= DELTA COMMANDS =================
@bot.command()
@commands.has_permissions(administrator=True)
async def annonce(ctx, *, message):
    embed = discord.Embed(title="📢 Delta Executor", description=message, color=0x00ffff, timestamp=datetime.now())
    await ctx.send("@everyone", embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def key(ctx, member: discord.Member = None):
    member = member or ctx.author
    key = "DELTA-" + "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=20))
    keys[key] = member.id
    await ctx.send(f"✅ Clé pour {member.mention}\n`{key}`")

@bot.command()
async def redeemkey(ctx):
    embed = discord.Embed(title="Redeem Delta Key", description="Clique pour entrer ta clé", color=0x00ffff)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="Entrer Clé", style=discord.ButtonStyle.green, custom_id="redeem_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def status(ctx):
    embed = discord.Embed(title="Delta Executor Status", color=0x00ff00)
    embed.add_field(name="Version", value="1.2", inline=True)
    embed.add_field(name="Statut", value="✅ Undetected", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def delta(ctx):
    await ctx.send("**Delta Executor v1.2** → ✅ Undetected")

@bot.command()
async def scripts(ctx):
    await ctx.send("**Scripts :** Infinite Yield, Fly, Godmode, Aimbot, ESP, Speed, Auto Farm...")

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
    await new.send("**Salon nuké** 🔥")

# ================= MODÉRATION =================
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
async def warn(ctx, member: discord.Member, *, reason="Aucune raison"):
    warns[member.id].append({"reason": reason, "time": str(datetime.now())})
   
    try:
        embed = discord.Embed(title="⚠️ Tu as reçu un Warn", color=0xff0000)
        embed.add_field(name="Serveur", value=ctx.guild.name, inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(name="Nombre total de warns", value=len(warns[member.id]), inline=False)
        embed.set_footer(text="Delta Executor")
        await member.send(embed=embed)
    except:
        await ctx.send(f"{member.mention} n'a pas pu recevoir le DM (DM fermés).", delete_after=5)
   
    await ctx.send(f"{member} a reçu un warn ({len(warns[member.id])}).")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted") or await ctx.guild.create_role(name="Muted")
    await member.add_roles(role)
    await ctx.send(f"{member} muté.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Salon verrouillé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Salon déverrouillé.")

# ================= MUSIC =================
@bot.command()
async def play(ctx, *, url: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Tu dois être dans un salon vocal.")

    try:
        voice_channel = ctx.author.voice.channel
        
        if ctx.voice_client is None:
            await voice_channel.connect()
            await ctx.send(f"✅ Connecté à **{voice_channel.name}**")
        else:
            if ctx.voice_client.channel != voice_channel:
                await ctx.voice_client.move_to(voice_channel)
                await ctx.send(f"✅ Déplacé vers **{voice_channel.name}**")

        await ctx.send(f"🎵 Lien reçu : {url}")
        await ctx.send("⚠️ **Impossible de jouer la musique pour le moment.**\n")
        await ctx.send("**Raison :** yt-dlp + ffmpeg ne sont pas installés sur Railway.")

    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

# ================= AUTRES =================
@bot.command()
async def memberinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=str(member), color=0x00ffff)
    embed.add_field(name="ID", value=member.id)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def balance(ctx):
    bal = economy[ctx.author.id]["balance"]
    await ctx.send(f"💰 Tu as **{bal}** Delta Coins.")

@bot.command()
async def daily(ctx):
    user = economy[ctx.author.id]
    now = datetime.now()
    if user["daily"] and (now - datetime.fromisoformat(user["daily"])).days < 1:
        return await ctx.send("Déjà pris aujourd'hui.")
    user["balance"] += 500
    user["daily"] = now.isoformat()
    await ctx.send("✅ +500 Delta Coins !")

# ================= LANCEMENT =================
if __name__ == "__main__":
    token = os.getenv("METS_TON_TOKEN_ICI")
    if not token:
        print("❌ Variable METS_TON_TOKEN_ICI non trouvée")
    else:
        bot.run(token)
