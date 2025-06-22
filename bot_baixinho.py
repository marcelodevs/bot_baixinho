import discord
from discord.ext import commands
import requests
import os

# Configurações Iniciais
TOKEN = os.getenv("DISCORD_BOT_TOKEN") or "coloque_seu_token_aqui"
PREFIX = "!"
CANAL_LOG = 1386352288808833094
CIDADES_SUPORTADAS = ["belo horizonte", "rio de janeiro", "fortaleza"]
API_CLIMA_KEY = os.getenv("OPENWEATHER_API_KEY") or "sua_chave_da_api_openweather"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Mensagem de boas-vindas
@bot.event
async def on_member_join(member):
    canal = bot.get_channel(CANAL_LOG)
    if canal:
        await canal.send(f"👋 Olá, {member.mention}! Bem-vindo ao servidor!")

# Log de saída
@bot.event
async def on_member_remove(member):
    canal = bot.get_channel(CANAL_LOG)
    if canal:
        await canal.send(f"🚪 {member.name} saiu do servidor.")

# Log de mensagens apagadas
@bot.event
async def on_message_delete(message):
    canal = bot.get_channel(CANAL_LOG)
    if canal and not message.author.bot:
        await canal.send(f"🗑️ Mensagem apagada de {message.author.mention} no canal {message.channel}: ```{message.content}```")

# Log de mensagens editadas
@bot.event
async def on_message_edit(before, after):
    canal = bot.get_channel(CANAL_LOG)
    if canal and not before.author.bot:
        await canal.send(f"✏️ Mensagem editada por {before.author.mention}: Antes: ```{before.content}``` Depois: ```{after.content}```")

# Clima (!clima <cidade>)
@bot.command(name="clima")
async def clima(ctx, *, cidade):
    cidade_lower = cidade.lower()
    if cidade_lower not in CIDADES_SUPORTADAS:
        await ctx.send(f"❌ Cidade não suportada. Tente uma dessas: {', '.join(CIDADES_SUPORTADAS)}")
        return

    url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_CLIMA_KEY}&lang=pt_br&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        descricao = data['weather'][0]['description'].capitalize()
        temperatura = data['main']['temp']
        await ctx.send(f"🌤️ Clima em {cidade.title()}: {descricao}, {temperatura}°C")
    else:
        await ctx.send("Erro ao obter informações do clima.")

# Comando !resenha
@bot.command(name="resenha")
async def resenha(ctx):
    frases = [
        "Alguém traz o violão! 🎸",
        "Cadê o churrasco, meu patrão? 🥩",
        "Resenha boa só se tiver meme novo 😎",
        "E se a gente fizesse um torneio de Uno? 🃏",
        "Hora da fofoca da semana 👀"
    ]
    import random
    await ctx.send(random.choice(frases))

# Comando !ping
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong! Estou online.")

bot.run(TOKEN)
