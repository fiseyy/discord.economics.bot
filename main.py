import datetime

import discord
from colorama import Fore, Style, init
from commands import setup
from discord.ext import commands

init()  # Initialize colorama

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

with open("token.txt", "r") as f:
    token = f.read().strip()

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    current_datetime = datetime.datetime.now()
    print(
        f"[{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}] [INFO    ] Logged in as {bot.user.name}"
    )
    print(
        f"{Fore.GREEN}[{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}] Started without errors!{Style.RESET_ALL}"
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "Команда не найдена. Пожалуйста, проверьте список команд с помощью `!help`."
        )
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send(
            f"У вас нет роли, необходимой для выполнения этой команды, {ctx.author.mention}!"
        )
    else:
        raise error


setup(bot)

bot.run(token)
