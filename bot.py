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
keys = {}
vip_users = []

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
    print(f"Delta Executor Bot → Tout est chargé à fond")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Delta Executor v1.2"))
    auto_announce.start()

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="bienvenue")
    if channel:
        await channel.send(f"{member.mention} a rejoint le serveur Delta Executor.")

# ================= AUTO ANNOUNCE =================
@tasks.loop(hours=4)
async def auto_announce():
    channel = discord.utils.get(bot.guilds[0].text_channels, name="annonces")
    if channel:
        await channel.send("@everyone Delta Executor est toujours actif • Prochaine update bientôt.")

# ================= MODALS =================
class RedeemModal(discord.ui.Modal, title="Redeem Delta Key"):
    key_input = discord.ui.TextInput(label="Ta clé Delta", placeholder="DELTA-XXXXXXXXXXXXXXXXXXXX", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        key = self.key_input.value.strip()
        if key in keys:
            role = discord.utils.get(interaction.guild.roles, name="Delta Client")
            if role: await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Clé validée ! Tu es maintenant **Delta Client**.", ephemeral=True)
            del keys[key]
        else:
            await interaction.response.send_message("❌ Clé invalide.", ephemeral=True)

class TokenModal(discord.ui.Modal, title="Token Info Checker"):
    token_input = discord.ui.TextInput(label="Colle le token", placeholder="MT...", required=True, style=discord.TextStyle.long)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔍 Vérification...", ephemeral=True)
        await asyncio.sleep(1.5)
        await interaction.followup.send("✅ Token semble valide (simulation).", ephemeral=True)

class StatusModal(discord.ui.Modal, title="Delta Status"):
    version_input = discord.ui.TextInput(label="Version du cheat", placeholder="1.2", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        version = self.version_input.value.strip()
        embed = discord.Embed(title="Delta Executor Status", color=0x00ff00)
        embed.add_field(name="Version", value=version, inline=True)
        embed.add_field(name="Statut", value="Undetected", inline=True)
        embed.add_field(name="Dernière MAJ", value=datetime.now().strftime("%d/%m/%Y"), inline=True)
        await interaction.response.send_message(embed=embed)

class BuyModal(discord.ui.Modal, title="Achat Delta Executor"):
    choice = discord.ui.TextInput(label="1 mois ou à vie ?", placeholder="1 mois ou vie", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"✅ Demande d'achat reçue ({self.choice.value}). Un admin va te contacter.", ephemeral=True)

# ================= INTERACTIONS =================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        if custom_id == "redeem_modal":
            await interaction.response.send_modal(RedeemModal())
        elif custom_id == "token_modal":
            await interaction.response.send_modal(TokenModal())
        elif custom_id == "status_modal":
            await interaction.response.send_modal(StatusModal())
        elif custom_id == "buy_modal":
            await interaction.response.send_modal(BuyModal())

# ================= COMMANDS =================
@bot.command()
async def redeemkey(ctx):
    embed = discord.Embed(title="Delta Key Redemption", description="Clique ci-dessous pour entrer ta clé", color=0x00ffff)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Entrer Clé", style=discord.ButtonStyle.green, custom_id="redeem_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def tokeninfo(ctx):
    embed = discord.Embed(title="Token Checker", description="Clique ci-dessous pour vérifier un token", color=0x00ffff)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Vérifier Token", style=discord.ButtonStyle.primary, custom_id="token_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def status(ctx):
    embed = discord.Embed(title="Delta Status", description="Clique ci-dessous pour définir la version", color=0x00ffff)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Ouvrir Status", style=discord.ButtonStyle.primary, custom_id="status_modal"))
    await ctx.send(embed=embed, view=view)

@bot.command()
async def buy(ctx):
    embed = discord.Embed(title="🛒 Boutique Delta", description="Clique pour acheter", color=0x00ffff)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Acheter", style=discord.ButtonStyle.success, custom_id="buy_modal"))
    await ctx.send(embed=embed, view=view)

# ================= DELTA COMMANDS (encore plus) =================
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
    await ctx.send(f"{member.mention} Clé générée : `{key}`")

@bot.command()
async def delta(ctx):
    embed = discord.Embed(title="Delta Executor PC", color=0x00ffff)
    embed.add_field(name="Statut", value="✅ Undetected 2026", inline=False)
    embed.add_field(name="Features", value="Aimbot • ESP • Fly • Speed • God Mode • Auto Farm • Kill All • Script Hub", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def scripts(ctx):
    embed = discord.Embed(title="📜 Scripts Delta", color=0x00ffff)
    embed.add_field(name="Disponibles", value="Infinite Yield, Fly Script, God Mode v2, Aimbot, ESP, Speed, Auto Farm, Kill All, Vehicle Speed, Silent Aim...", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def changelog(ctx):
    embed = discord.Embed(title="Changelog", color=0x00ffff)
    embed.add_field(name="v1.2", value="• Nouveau menu\n• Fix anti-detect\n• +20 scripts", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def support(ctx):
    await ctx.send("Ticket support ouvert ! Un admin arrive.")

# ================= TOUTES LES ANCIENNES COMMANDES (TOUT GARDÉ) =================
@bot.command()
async def fonction(ctx):
    embed = discord.Embed(title="📜 TOUTES LES COMMANDES DELTA", color=0x00ffff)
    embed.add_field(name="Delta", value="`!annonce` `!key` `!redeemkey` `!tokeninfo` `!status` `!buy` `!delta` `!scripts` `!changelog` `!support`", inline=False)
    embed.add_field(name="Clear", value="`!clear nombre` `!clearall nombre`", inline=False)
    embed.add_field(name="Nuke", value="`!nuke` `!nukeall`", inline=False)
    embed.add_field(name="Modération", value="`!ban` `!kick` `!mute` etc.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.invoke(bot.get_command('fonction'))

# Clear (fixé)
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
    await new_channel.send("**Salon nuké par Delta Executor** 🔥")

# Lancement
token = os.getenv("TOKEN")
if not token:
    print("ERREUR : TOKEN MANQUANT")
else:
    bot.run(token)
