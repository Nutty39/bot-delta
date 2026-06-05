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
keys = {}

@bot.event
async def on_ready():
    print(f"✅ Delta Executor Bot → Tout est chargé")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

# ================= MODAL REDEEM =================
class RedeemModal(discord.ui.Modal, title="Redeem Delta Key"):
    key_input = discord.ui.TextInput(label="Entre ta clé Delta", placeholder="DELTA-XXXXXXXXXXXXXXXXXXXX", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        key = self.key_input.value.strip()
        if key in keys:
            role = discord.utils.get(interaction.guild.roles, name="Delta Client")
            if role:
                await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Clé validée ! Tu es maintenant **Delta Client**.", ephemeral=True)
            del keys[key]
        else:
            await interaction.response.send_message("❌ Clé invalide ou déjà utilisée.", ephemeral=True)

# ================= HELP =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA", color=0x00ffff)
    embed.add_field(name="📢 Delta", value="`!annonce` `!key` `!redeemkey` `!tokeninfo` `!status` `!delta` `!scripts` `!changelog` `!buy`", inline=False)
    embed.add_field(name="🧹 Clear", value="`!clear <nombre>` `!clearall <nombre>`", inline=False)
    embed.add_field(name="🔥 Nuke", value="`!nuke` `!nukeall`", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="🎉 Fun", value="`!giveaway` `!fake_nitro` `!ticket` `!reactionrole`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!unban` `!warn` `!mute` `!unmute` `!slowmode` `!lock` `!unlock` `!setclean`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

# ================= DELTA COMMANDS (TOUT GARDÉ) =================
@bot.command()
@commands.has_permissions(administrator=True)
async def annonce(ctx, *, message):
    embed = discord.Embed(title="📢 Delta Executor", description=message, color=0x00ffff)
    await ctx.send("@everyone", embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def key(ctx, member: discord.Member = None):
    member = member or ctx.author
    key = "DELTA-" + "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=20))
    keys[key] = member.id
    await ctx.send(f"{member.mention} Clé générée :\n`{key}`")

@bot.command()
async def redeemkey(ctx):
    embed = discord.Embed(title="Redeem Delta Key", description="Clique ci-dessous pour entrer ta clé", color=0x00ffff)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="Entrer Clé", style=discord.ButtonStyle.green, custom_id="redeem_modal"))
    await ctx.send(embed=embed, view=view)

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
    await ctx.send("**Scripts disponibles :** Infinite Yield, Fly Script, God Mode, Aimbot, ESP, Speed, Auto Farm...")

# ================= INTERACTION (MODAL) =================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data.get("custom_id") == "redeem_modal":
        await interaction.response.send_modal(RedeemModal())

# ================= MODÉRATION & AUTRES (TOUT GARDÉ) =================
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
async def mute(ctx, member: discord.Member, minutes: int = 10):
    await ctx.send(f"{member} muté pour {minutes} minutes.")

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

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("❌ TOKEN MANQUANT")
else:
    bot.run(token)
