import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# Функция для сохранения и загрузки данных о балансе пользователей
def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)


def load_data():
    with open("data.json", "r") as f:
        return json.load(f)


# Команда для проверки баланса
@bot.command()
async def balance(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    balance = data.get(user_id, 0)
    await ctx.send(f"{ctx.author.mention}, ваш баланс: {balance} монет.")


# Команда для добавления монет пользователю
@bot.command()
@commands.has_permissions(administrator=True)
async def add_coins(ctx, member: discord.Member, amount: int):
    data = load_data()
    user_id = str(member.id)
    data[user_id] = data.get(user_id, 0) + amount
    save_data(data)
    await ctx.send(f"{member.mention}, вам было добавлено {amount} монет.")


# Команда для покупки предмета
@bot.command()
async def buy(ctx, item_name: str):
    data = load_data()
    user_id = str(ctx.author.id)
    balance = data.get(user_id, 0)

    # Список предметов и их стоимость
    store_items = {
        "item1": 100,
        "item2": 200,
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
bot.run("ваш_токен_бота")
