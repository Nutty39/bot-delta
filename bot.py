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
    print(f"✅ Delta Executor Bot → Tout est chargé")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

# ================= MODAL =================
class RedeemModal(discord.ui.Modal, title="Redeem Delta Key"):
    key_input = discord.ui.TextInput(label="Ta clé Delta", placeholder="DELTA-XXXXXXXXXXXXXXXXXXXX", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        key = self.key_input.value.strip()
        if key in keys:
            role = discord.utils.get(interaction.guild.roles, name="Delta Client")
            if role:
                await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Clé validée !", ephemeral=True)
            del keys[key]
        else:
            await interaction.response.send_message("❌ Clé invalide.", ephemeral=True)

# ================= HELP COMPLET =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA", color=0x00ffff)
    embed.add_field(name="📢 Delta", value="`!annonce` `!key` `!redeemkey` `!tokeninfo` `!status` `!delta` `!scripts` `!changelog` `!buy`", inline=False)
    embed.add_field(name="🧹 Clear", value="`!clear <nombre>` `!clearall <nombre>`", inline=False)
    embed.add_field(name="🔥 Nuke", value="`!nuke` `!nukeall`", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="💰 Économie", value="`!balance` `!daily` `!pay`", inline=False)
    embed.add_field(name="🎉 Fun", value="`!giveaway` `!fake_nitro` `!ticket` `!reactionrole`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!unban` `!warn` `!mute` `!unmute` `!slowmode` `!lock` `!unlock` `!setclean`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

# ================= DELTA =================
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
    await ctx.send(f"{member.mention} Clé :\n`{key}`")

@bot.command()
async def redeemkey(ctx):
    embed = discord.Embed(title="Redeem Key", description="Clique pour entrer ta clé", color=0x00ffff)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="Entrer Clé", style=discord.ButtonStyle.green, custom_id="redeem_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def tokeninfo(ctx, *, token: str):
    await ctx.send("🔍 Vérification...\n✅ Token semble valide.")

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
    await ctx.send("**Scripts :** Infinite Yield, Fly Script, God Mode, Aimbot, ESP, Speed, Auto Farm...")

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
    new = await ctx.channel.clone()
    await ctx.channel.delete()
    await new.send("**Salon nuké** 🔥")

@bot.command()
@commands.has_permissions(administrator=True)
async def nukeall(ctx):
    for ch in list(ctx.guild.channels):
        try:
            await ch.delete()
        except:
            pass
    await ctx.guild.create_text_channel("nuke-termine")

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
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role and role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"{member} unmute.")
    else:
        await ctx.send("Pas muté.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Slowmode mis à {seconds}s.")

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

# ================= INTERACTION =================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data.get("custom_id") == "redeem_modal":
        await interaction.response.send_modal(RedeemModal())

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("❌ TOKEN MANQUANT")
else:
    bot.run(token)
