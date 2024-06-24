import discord
from discord.ext import commands
import json
import os
import random
from discord.ext.commands import cooldown

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Функция для сохранения и загрузки данных о балансе пользователей
def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)


def load_data():
    if not os.path.exists("data.json"):
        with open("data.json", "w") as f:
            json.dump({}, f)
    with open("data.json", "r") as f:
        return json.load(f)


# Команда для проверки баланса
@bot.command()
async def balance(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data:
        data[user_id] = 0
        save_data(data)
    balance = data.get(user_id, 0)
    await ctx.send(f"{ctx.author.mention}, ваш баланс: {balance} монет.")


@bot.command()
async def hi(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}")


# Команда для добавления монет пользователю
@bot.command()
@commands.has_permissions(administrator=True)
# @commands.has_any_role(ROLE ID) - если надо по отдельному id роли
async def add_coins(ctx, member: discord.Member, amount: int):
    data = load_data()
    user_id = str(member.id)
    if user_id not in data:
        data[user_id] = 0
        save_data(data)
    data[user_id] += amount
    save_data(data)
    await ctx.send(f"{member.mention}, вам было добавлено {amount} монет.")


@bot.command()
async def work_list(ctx):
    embed = discord.Embed(
        title="Список работ",
        description="Выберите работу",
    )
    embed.add_field(name="банкир", value="100 монет", inline=True)
    embed.add_field(name="полицейский", value="500 монет шансом 66%", inline=True)
    embed.add_field(name="пожарный", value="300 монет шансом 87%", inline=True)
    await ctx.send(embed=embed)


@bot.command()
@cooldown(1, 1200, commands.BucketType.user)
async def work(ctx, work_type: str):
    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data:
        data[user_id] = 0
        save_data(data)
    balance = data.get(user_id, 0)
    match work_type:
        case "банкир":
            data[user_id] += 100
            f"{ctx.author.mention}, Вы заработали 100 монет."
        case "полицейский":
            # шанс 33% потерять 75% денег
            data[user_id] += 500
            if random.randint(1, 3) == 1:
                data[user_id] -= int(500 * 0.75)
                await ctx.send(
                    f"{ctx.author.mention}, О нет! Преступник украл у вас часть вашей зарплаты! Вы заработали 125 монет."
                )
            else:
                await ctx.send(
                    f"{ctx.author.mention}, Вы молодец! Вы заработали 500 монет."
                )
        case "пожарный":
            # шанс 12% потерять 60% денег
            data[user_id] += 300
            if random.randint(1, 8) == 1:
                data[user_id] -= int(300 * 0.60)
                await ctx.send(
                    f"{ctx.author.mention}, О нет! У вас при пожаре выпал кошелек! Вы заработали 120 монет."
                )
            else:
                await ctx.send(
                    f"{ctx.author.mention}, Вы молодец! Вы заработали 300 монет."
                )
        case _:
            await ctx.send(
                f"{ctx.author.mention}, неизвестная работа. Пожалуйста, выберите из списка работ. (!work_list)"
            )
    save_data(data)


@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cooldown_time = error.retry_after
        minutes, seconds = divmod(cooldown_time, 60)
        await ctx.send(
            f"Вы должны подождать {round(minutes,0)} минут и {round(seconds, 0)} секунд перед использованием этой команды снова."
        )
    else:
        raise error


# Команда для покупки предмета
@bot.command()
async def buy(ctx, item_name: str):
    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data:
        data[user_id] = 0
        save_data(data)
    balance = data.get(user_id, 0)

    # Список предметов и их стоимость
    store_items = {
        "телефон": 100,
        "планшет": 200,
        "ноутбук": 500,
        # Добавьте больше предметов и их стоимость здесь
    }

    # Проверяем, есть ли предмет в магазине
    if item_name in store_items:
        item_cost = store_items[item_name]
        if balance >= item_cost:
            data[user_id] -= item_cost
            save_data(data)
            await ctx.send(
                f"{ctx.author.mention}, вы успешно купили {item_name} за {item_cost} монет."
            )
        else:
            await ctx.send(
                f"{ctx.author.mention}, недостаточно средств для покупки {item_name}."
            )
    else:
        await ctx.send(
            f"{ctx.author.mention}, предмет {item_name} не найден в магазине."
        )


# Запускаем бота
bot.run("TOKEN")
