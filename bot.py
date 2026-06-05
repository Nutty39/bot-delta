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
    print(f"✅ Delta Executor Bot → Connecté")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))

# ================= MODAL REDEEM (gardé) =================
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

# ================= COMMANDES CORRIGÉES =================
@bot.command()
@commands.has_permissions(administrator=True)
async def annonce(ctx, *, message):
    embed = discord.Embed(title="📢 Delta Executor", description=message, color=0x00ffff, timestamp=datetime.now())
    embed.set_footer(text="Official Delta Executor")
    await ctx.send("@everyone", embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong ! Latence : **{round(bot.latency * 1000)}ms**")

@bot.command()
async def memberinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    embed = discord.Embed(title=f"Infos → {member}", color=0x00ffff)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Pseudo", value=str(member), inline=True)
    embed.add_field(name="Rejoint le", value=member.joined_at.strftime("%d/%m/%Y %H:%M") if member.joined_at else "Inconnu", inline=True)
    embed.add_field(name="Créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Rôles", value=", ".join(roles)[:500] or "Aucun", inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# ================= LE RESTE (TOUT GARDÉ) =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="🚀 TOUTES LES COMMANDES DELTA", color=0x00ffff)
    embed.add_field(name="📢 Delta", value="`!annonce` `!key` `!redeemkey` `!tokeninfo` `!status` `!delta` `!scripts`", inline=False)
    embed.add_field(name="🧹 Clear", value="`!clear <nombre>` `!clearall <nombre>`", inline=False)
    embed.add_field(name="🔥 Nuke", value="`!nuke` `!nukeall`", inline=False)
    embed.add_field(name="👤 Infos", value="`!memberinfo` `!avatar` `!level` `!leaderboard`", inline=False)
    embed.add_field(name="🎉 Fun", value="`!giveaway` `!fake_nitro` `!ticket` `!reactionrole`", inline=False)
    embed.add_field(name="🛠️ Modération", value="`!ban` `!kick` `!unban` `!warn` `!mute` `!unmute` `!slowmode` `!lock` `!unlock` `!setclean`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

@bot.command()
async def redeemkey(ctx):
    embed = discord.Embed(title="Redeem Key", description="Clique pour entrer ta clé", color=0x00ffff)
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="Entrer Clé", style=discord.ButtonStyle.green, custom_id="redeem_modal"))
    await ctx.send(embed=embed, view=view)

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
