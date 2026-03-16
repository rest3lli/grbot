import discord
from discord.ext import commands
import sqlite3
import datetime
from dotenv import load_dotenv
import os
import pip_system_certs.wrapt_requests

# carrega o .env
load_dotenv()

# conectar ou criar banco
conexao = sqlite3.connect("bot.db")
cursor = conexao.cursor()

# criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    mensagem TEXT,
    data TEXT
)
""")
conexao.commit()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# MENU COM BOTÕES
class Menu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👋 Dizer Oi", style=discord.ButtonStyle.primary)
    async def botao_oi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Oi! Você clicou no botão 😄")

    @discord.ui.button(label="🕒 Ver Hora", style=discord.ButtonStyle.success)
    async def botao_hora(self, interaction: discord.Interaction, button: discord.ui.Button):
        hora = datetime.datetime.now().strftime("%H:%M")
        await interaction.response.send_message(f"Agora são {hora}")

    @discord.ui.button(label="📜 Histórico", style=discord.ButtonStyle.secondary)
    async def botao_historico(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT usuario, mensagem FROM mensagens ORDER BY id DESC LIMIT 5")
        resultados = cursor.fetchall()

        resposta = "Últimas mensagens:\n"
        for r in resultados:
            resposta += f"{r[0]}: {r[1]}\n"

        await interaction.response.send_message(resposta)

# comando para abrir menu
@bot.command()
async def menu(ctx):
    await ctx.send("Escolha uma opção:", view=Menu())

@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    usuario = str(message.author)
    msg = message.content.lower()
    data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    cursor.execute(
        "INSERT INTO mensagens (usuario, mensagem, data) VALUES (?, ?, ?)",
        (usuario, msg, data)
    )
    conexao.commit()

    if "oi" in msg:
        await message.channel.send("Oi! Tudo bem? 😄")

    await bot.process_commands(message)

# SEMPRE POR ÚLTIMO
bot.run(os.getenv("TOKEN"))
