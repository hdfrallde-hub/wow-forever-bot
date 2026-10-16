import discord
from discord.ext import commands
from discord.ui import Button, View
from flask import Flask
from threading import Thread
import os

# ----------------- UPTIME/WEBBSERVER KOD -----------------
# Detta håller botten vid liv på gratis molntjänster
app = Flask('')

@app.route('/')
def home():
    return "Botten är vid liv!"

def run_webserver():
    # Render använder miljövariabeln PORT, annars defaultar vi till 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_webserver)
    t.start()
# ---------------------------------------------------------

# Hämta din Discord Token säkert från molntjänstens inställningar (rekommenderas!)
# Om du testar lokalt kan du temporärt byta ut detta mot: TOKEN = "DIN_TOKEN"
TOKEN = os.environ.get('DISCORD_TOKEN', 'DIN_TEMPORÄRA_TOKEN_HÄR')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 1. Knappar för Fraktioner
class FactionView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Horde", style=discord.ButtonStyle.danger, custom_id="role_horde")
    async def horde_button(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Horde")
        await toggle_role(interaction, role, "Horde")

    @discord.ui.button(label="Alliance", style=discord.ButtonStyle.primary, custom_id="role_alliance")
    async def alliance_button(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Alliance")
        await toggle_role(interaction, role, "Alliance")

# 2. Knappar för Klassroller
class ClassRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛡️ Tank", style=discord.ButtonStyle.secondary, custom_id="role_tank")
    async def tank_button(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Tank")
        await toggle_role(interaction, role, "Tank")

    @discord.ui.button(label="🟢 Healer", style=discord.ButtonStyle.success, custom_id="role_healer")
    async def healer_button(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Healer")
        await toggle_role(interaction, role, "Healer")

    @discord.ui.button(label="⚔️ DPS", style=discord.ButtonStyle.danger, custom_id="role_dps")
    async def dps_button(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="DPS")
        await toggle_role(interaction, role, "DPS")

async def toggle_role(interaction: discord.Interaction, role: discord.Role, role_name: str):
    if not role:
        await interaction.response.send_message(f"Hittade inte rollen '{role_name}' på servern. Skapa den i serverinställningarna först!", ephemeral=True)
        return
    if role in interaction.user.roles:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"Du har tagit bort rollen **{role_name}**.", ephemeral=True)
    else:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"Du har fått rollen **{role_name}**!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Botten är online som {bot.user}")
    bot.add_view(FactionView())
    bot.add_view(ClassRoleView())
    try:
        await bot.tree.sync()
        print("Synkade snedstreckskommandon.")
    except Exception as e:
        print(f"Kunde inte synka kommandon: {e}")

@bot.tree.command(name="skicka_rollmeny", description="Skickar menyerna för att välja WoW-roller.")
@commands.has_permissions(administrator=True)
async def skicka_rollmeny(interaction: discord.Interaction):
    await interaction.response.send_message("Skapar menyer...", ephemeral=True)
    await interaction.channel.send("### 🌍 Välj din fraktion:", view=FactionView())
    await interaction.channel.send("### 🛡️ Välj din roll i raids/dungeons:", view=ClassRoleView())

# Starta webbservern först, sedan botten
keep_alive()
bot.run(TOKEN)
