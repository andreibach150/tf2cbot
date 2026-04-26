import os
from pathlib import Path
import socket

import discord
from discord import app_commands
from discord.ext import tasks
import a2s

def carregar_env(caminho_arquivo: str = ".env") -> None:
    env_path = Path(caminho_arquivo)
    if not env_path.is_absolute():
        env_path = Path(__file__).resolve().with_name(caminho_arquivo)

    if not env_path.exists():
        return

    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue

        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip("\"'")
        os.environ.setdefault(chave, valor)


carregar_env()
bot_token = os.getenv("DISCORD_TOKEN")
status_channel_id = os.getenv("STATUS_CHANNEL_ID")
STATUS_CHANNEL_ID = int(status_channel_id) if status_channel_id else None

if not bot_token:
    raise RuntimeError(
        "A variavel DISCORD_TOKEN nao foi encontrada. "
        "Coloque o token no arquivo .env ou defina a variavel de ambiente."
    )


SERVERS = [
    ("177.74.185.42", 27040),
    ("177.74.185.42", 27050),
    ("177.74.185.42", 27015),
    ("142.44.137.212", 28001),
    ("169.254.108.77", 65376),
    ("192.99.105.48", 27015),
    ("192.99.105.48", 27017),
    ("192.99.105.49", 27015),
    ("192.99.105.50", 27015),
    ("54.39.130.18", 27015),
]


async def criar_embed_servidores() -> discord.Embed:
    embed = discord.Embed(
        title="Status dos servidores",
        color=discord.Color.green()
    )

    for address in SERVERS:
        ip, port = address

        try:
            info = await a2s.ainfo(address, timeout=10.0)
            texto = (
                f"Nome: {info.server_name}\n"
                f"Mapa: {info.map_name}\n"
                f"Jogadores: {info.player_count}/{info.max_players}"
            )
        except (socket.timeout, TimeoutError):
            texto = "TIMEOUT"
        except ConnectionRefusedError:
            texto = "CONEXAO FECHADA"
        except Exception as e:
            texto = f"ERRO: {type(e).__name__}: {e}"

        embed.add_field(
            name=f"{ip}:{port}",
            value=texto,
            inline=False
        )

    return embed


class MeuPrimeiroBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        if STATUS_CHANNEL_ID and not ping_servers_loop.is_running():
            ping_servers_loop.start()

    async def on_ready(self):
        print(f"{self.user} esta ONLINE!")
        if STATUS_CHANNEL_ID:
            print(f"Envio automatico a cada hora no canal {STATUS_CHANNEL_ID}.")
        else:
            print("STATUS_CHANNEL_ID nao definido. Envio automatico desativado.")


bot = MeuPrimeiroBot()


@tasks.loop(hours=1)
async def ping_servers_loop():
    if not STATUS_CHANNEL_ID:
        return

    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(STATUS_CHANNEL_ID)
        except Exception as e:
            print(f"Nao foi possivel acessar o canal {STATUS_CHANNEL_ID}: {e}")
            return

    embed = await criar_embed_servidores()
    await channel.send(embed=embed)


@ping_servers_loop.before_loop
async def before_ping_servers_loop():
    await bot.wait_until_ready()


@bot.tree.command(name="ajuda", description="mostra alguns comandos do bot")
async def ajuda(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**COMANDOS**\n"
        "**/pingservers** (PINGA ALGUNS SERVIDORES)\n"
    )

@bot.tree.command(name="pingservers", description="Verifica alguns servidores de TF2C")
async def ping_servers(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = await criar_embed_servidores()
    await interaction.followup.send(embed=embed)

bot.run(bot_token)
