import discord
from discord.ext import commands
from commands import setup

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "Команда не найдена. Пожалуйста, проверьте список команд с помощью `!help`."
        )
    else:
        raise error


# bot.load_extension("commands")
setup(bot)

bot.run("TOKEN")
