import discord
from discord.ext import commands
import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= DATA =================
levels = defaultdict(lambda: {"xp": 0, "level": 1})
warns = defaultdict(list)
economy = defaultdict(lambda: {"balance": 100, "daily": None})
keys = {}
config = {}

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Delta Executor Bot → Connecté en tant que {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Système de niveaux
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
            await interaction.response.send_message("✅ Clé validée ! Tu as maintenant le rôle Delta Client.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Clé invalide ou déjà utilisée.", ephemeral=True)

# ================= HELP COMPLET =================
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA EXECUTOR", color=0x00ffff)
    embed.add_field(name="📢 Delta", value="`!annonce` `!key` `!redeemkey` `!status` `!delta` `!scripts` `!tokeninfo`", inline=False)
    embed.add_field(name="🧹 Clear & Nuke", value="`!clear` `!clearall` `!nuke` `!nukeall`", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="💰 Économie", value="`!balance` `!daily` `!pay`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!warn` `!mute` `!unmute` `!slowmode` `!lock` `!unlock`", inline=False)
    embed.set_footer(text="Delta Executor v1.2 - Tout est là enfoiré")
    await ctx.send(embed=embed)

@bot.command()
async def fonction(ctx):
    await ctx.invoke(bot.get_command('help'))

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
    await ctx.send(f"✅ Clé générée pour {member.mention}\n`{key}`")

@bot.command()
async def redeemkey(ctx):
    embed = discord.Embed(title="Redeem Delta Key", description="Clique ci-dessous pour entrer ta clé", color=0x00ffff)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="Entrer Clé", style=discord.ButtonStyle.green, custom_id="redeem_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def tokeninfo(ctx, *, token: str):
    await ctx.send("🔍 Vérification du token...\n✅ Token semble valide (simulation).")

@bot.command()
async def status(ctx):
    embed = discord.Embed(title="Delta Executor Status", color=0x00ff00)
    embed.add_field(name="Version", value="1.2", inline=True)
    embed.add_field(name="Statut", value="✅ Undetected", inline=True)
    embed.add_field(name="Date", value="Juin 2026", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def delta(ctx):
    embed = discord.Embed(title="Delta Executor", description="**Le meilleur executor gratuit 2026**", color=0x00ffff)
    embed.add_field(name="Statut", value="✅ Undetected", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def scripts(ctx):
    await ctx.send("**Scripts disponibles :** Infinite Yield, Fly, Godmode, Aimbot, ESP, Speed Hack, Auto Farm, etc.")

# ================= CLEAR & NUKE =================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages supprimés.", delete_after=4)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearall(ctx, amount: int = 50):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages virés.", delete_after=4)

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    new_channel = await ctx.channel.clone()
    await ctx.channel.delete()
    await new_channel.send("**Salon nuké avec succès** 🔥")

@bot.command()
@commands.has_permissions(administrator=True)
async def nukeall(ctx):
    for channel in list(ctx.guild.channels):
        try:
            await channel.delete()
        except:
            pass
    await ctx.guild.create_text_channel("nuke-termine")

# ================= MODÉRATION =================
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} a été banni.")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.kick(reason=reason)
    await ctx.send(f"{member} a été kick.")

@bot.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member, *, reason="Aucune raison"):
    warns[member.id].append({"reason": reason, "time": datetime.now().isoformat()})
    await ctx.send(f"{member} a reçu un warn. Total : **{len(warns[member.id])}**")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for ch in ctx.guild.channels:
            await ch.set_permissions(role, send_messages=False, speak=False)
    await member.add_roles(role)
    await ctx.send(f"{member} a été muté.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role and role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"{member} a été unmute.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Slowmode mis à {seconds} secondes.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Salon verrouillé 🔒")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Salon déverrouillé 🔓")

# ================= INFOS =================
@bot.command()
async def memberinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"Info de {member}", color=0x00ffff)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Créé le", value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Rejoint le", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "N/A")
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.display_avatar.url)

@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = levels[member.id]
    embed = discord.Embed(title=f"Niveau de {member}", color=0x00ff00)
    embed.add_field(name="Niveau", value=data["level"])
    embed.add_field(name="XP", value=f"{data['xp']}/{data['level'] * 100}")
    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    sorted_levels = sorted(levels.items(), key=lambda x: x[1]["level"], reverse=True)[:10]
    desc = "\n".join([f"{i+1}. <@{user}> - Niveau {data['level']}" for i, (user, data) in enumerate(sorted_levels)])
    embed = discord.Embed(title="🏆 Leaderboard Niveaux", description=desc or "Aucun joueur", color=0x00ffff)
    await ctx.send(embed=embed)

# ================= ECONOMY =================
@bot.command()
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    bal = economy[member.id]["balance"]
    await ctx.send(f"💰 {member.mention} a **{bal}** Delta Coins.")

@bot.command()
async def daily(ctx):
    user = economy[ctx.author.id]
    now = datetime.now()
    if user["daily"] and now - datetime.fromisoformat(user["daily"]) < timedelta(days=1):
        await ctx.send("⏳ Tu as déjà récupéré ton daily aujourd'hui.")
        return
    user["balance"] += 500
    user["daily"] = now.isoformat()
    await ctx.send("✅ Tu as reçu **500** Delta Coins ! Reviens demain.")

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        return await ctx.send("Montant invalide.")
    if economy[ctx.author.id]["balance"] < amount:
        return await ctx.send("Tu n'as pas assez d'argent.")
    economy[ctx.author.id]["balance"] -= amount
    economy[member.id]["balance"] += amount
    await ctx.send(f"✅ Tu as donné **{amount}** Delta Coins à {member.mention}.")

# ================= LANCEMENT =================
bot.run("METS_TON_TOKEN_ICI")   # ← Remplace par ton vrai token
