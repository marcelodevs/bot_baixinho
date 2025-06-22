import discord
from discord.ext import commands
from discord.ui import View, Button
import requests
import os

# Configurações Iniciais
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = "!"
CANAL_LOG = 1386352288808833094
CANAL_WELCOME = 1386353310604333091
API_CLIMA_KEY = os.getenv("OPENWEATHER_API_KEY")

print(f"Token carregado: {TOKEN}")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Mensagem de boas-vindas
@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.text_channels, name="geral")
    if canal:
        embed = discord.Embed(
            title=f"👋 Bem-vindo ao servidor!",
            description=f"{member.mention}, esperamos que você aproveite sua estadia!",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Usuário: {member.name}#{member.discriminator}", icon_url=member.avatar.url)
        await canal.send(embed=embed)

# Log de saída
@bot.event
async def on_member_remove(member):
    canal = bot.get_channel(CANAL_LOG)
    if canal:
        await canal.send(f"```{member.name} saiu do servidor.```")

# Log de mensagens apagadas
@bot.event
async def on_message_delete(message):
    canal = bot.get_channel(CANAL_LOG)
    if canal and not message.author.bot:
        await canal.send(f"🗑️ Mensagem apagada no canal {message.channel}: ```{message.author}: {message.content}```")

# Log de mensagens editadas
@bot.event
async def on_message_edit(before, after):
    canal = bot.get_channel(CANAL_LOG)
    if canal and not before.author.bot:
        await canal.send(f"✏️ Mensagem editada por {before.author}: Antes: ```{before.content}``` Depois: ```{after.content}```")

# Clima (!clima <cidade>)
@bot.command(name="clima")
async def clima(ctx, *, cidade):
    cidade_lower = cidade.lower()

    url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade_lower}&appid={API_CLIMA_KEY}&lang=pt_br&units=metric"
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

# Lista de cargos de cor disponíveis
CORES_DISPONIVEIS = {
    "🔴 Vermelho": "Vermelho",
    "🔵 Azul": "Azul",
    "🟢 Verde": "Verde",
    "⚫ Preto": "Preto",
    "🐷 Rosa": "Rosa",
    "🟣 Roxo": "Roxo",
    "🟡 Amarelo": "Amarelo",
    "🟠 Laranja": "Laranja"
}

@bot.command(name="cores")
async def escolher_cor(ctx):
    class CoresView(View):
        def __init__(self):
            super().__init__(timeout=None)
            for emoji_nome, nome_cargo in CORES_DISPONIVEIS.items():
                emoji, _ = emoji_nome.split(" ", 1)
                self.add_item(ColorButton(emoji, nome_cargo))

    await ctx.send("🎨 Escolha sua cor clicando em um botão:\n", view=CoresView())

class ColorButton(Button):
    def __init__(self, emoji, role_name):
        super().__init__(style=discord.ButtonStyle.primary, emoji=emoji, label=role_name)
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        # Remove outras cores
        roles_to_remove = [role for role in member.roles if role.name in CORES_DISPONIVEIS.values()]
        await member.remove_roles(*roles_to_remove)

        # Dá a nova cor
        role = discord.utils.get(guild.roles, name=self.role_name)
        if not role:
            # Se o cargo não existir, cria
            role = await guild.create_role(name=self.role_name)
            print(f"Criado novo cargo: {self.role_name}")

        await member.add_roles(role)
        await interaction.response.defer(ephemeral=True)

bot.run(TOKEN)
