import asyncio
import json
import os
import random

import discord
from discord.ext import commands, tasks
from discord.ext.commands import BucketType, cooldown

store_items = {
    "телефон": 100,
    "планшет": 200,
    "ноутбук": 500,
}

properties = {
    "киоск": {"cost": 1000, "income": 50},
    "магазин": {"cost": 5000, "income": 250},
    "торговый центр": {"cost": 20000, "income": 1000},
}

data_lock = asyncio.Lock()


async def save_data(data):
    async with data_lock:
        with open("data.json", "w") as f:
            json.dump(data, f)


async def load_data():
    if not os.path.exists("data.json"):
        async with data_lock:
            with open("data.json", "w") as f:
                json.dump({}, f)
    async with data_lock:
        with open("data.json", "r") as f:
            return json.load(f)


def setup(bot):
    @bot.event
    async def on_ready():
        daily_income.start()

    @bot.command(name="help")
    async def help_command(ctx):
        embed = discord.Embed(
            title="Команды бота:", description="", color=discord.Colour.blue()
        )
        commands = [
            ("help", "Отобразить это меню"),
            ("balance", "Отобразить ваш баланс"),
            ("add_coins <человек> <количество>", "Добавляет денег человеку"),
            ("work <работа>", "Работать (cooldown 20 минут)"),
            ("work_list", "Список работ"),
            ("hi", "Бот поприветствует вас"),
            ("shop", "Показывает вещи, которые вы можете купить"),
            ("buy <название предмета>", "Купить предмет"),
            ("property_list", "Показать доступные для покупки недвижимости"),
            ("buy_property <название>", "Купить недвижимость"),
            ("properties", "Показать вашу недвижимость"),
            ("guess", "Мини-игра 'Угадай число'"),
        ]
        for cmd, desc in commands:
            embed.add_field(name=f"!{cmd}", value=desc, inline=False)
        await ctx.send(embed=embed)

    @bot.command(name="balance", help="Отобразить ваш баланс")
    async def balance(ctx):
        data = await load_data()
        user_id = str(ctx.author.id)
        balance = data.get(user_id, {}).get("balance", 0)
        await ctx.send(f"{ctx.author.mention}, ваш баланс: {balance} монет.")

    @bot.command(name="hi", help="Бот поприветствует вас")
    async def hi(ctx):
        await ctx.send(f"Привет, {ctx.author.mention}")

    @bot.command(name="add_coins", help="Добавляет денег человеку")
    @commands.has_any_role(1254537543458885752)
    async def add_coins(ctx, member: discord.Member, amount: int):
        data = await load_data()
        user_id = str(member.id)
        if user_id not in data:
            data[user_id] = {"balance": 0, "properties": []}
        data[user_id]["balance"] += amount
        await save_data(data)
        await ctx.send(f"{member.mention}, вам было добавлено {amount} монет.")

    @bot.command(name="work_list", help="Список работ")
    async def work_list(ctx):
        embed = discord.Embed(title="Список работ", description="Выберите работу")
        embed.add_field(name="банкир", value="100 монет", inline=True)
        embed.add_field(name="полицейский", value="500 монет шансом 66%", inline=True)
        embed.add_field(name="пожарный", value="300 монет шансом 87%", inline=True)
        await ctx.send(embed=embed)

    @bot.command(name="work", help="Работать (cooldown 20 минут)")
    @cooldown(1, 1200, BucketType.user)
    async def work(ctx, work_type: str):
        data = await load_data()
        user_id = str(ctx.author.id)
        if user_id not in data:
            data[user_id] = {"balance": 0, "properties": []}

        balance = data[user_id]["balance"]
        result = ""
        if work_type == "банкир":
            balance += 100
            result = f"{ctx.author.mention}, Вы заработали 100 монет."
        elif work_type == "полицейский":
            if random.randint(1, 3) == 1:
                balance += 125
                result = f"{ctx.author.mention}, О нет! Преступник украл у вас часть вашей зарплаты! Вы заработали 125 монет."
            else:
                balance += 500
                result = f"{ctx.author.mention}, Вы молодец! Вы заработали 500 монет."
        elif work_type == "пожарный":
            if random.randint(1, 8) == 1:
                balance += 120
                result = f"{ctx.author.mention}, О нет! У вас при пожаре выпал кошелек! Вы заработали 120 монет."
            else:
                balance += 300
                result = f"{ctx.author.mention}, Вы молодец! Вы заработали 300 монет."
        else:
            result = f"{ctx.author.mention}, неизвестная работа. Пожалуйста, выберите из списка работ. (!work_list)"

        data[user_id]["balance"] = balance
        await save_data(data)
        await ctx.send(result)

    @work.error
    async def work_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            await ctx.send(
                f"Вы должны подождать {int(minutes)} минут и {int(seconds)} секунд перед использованием этой команды снова."
            )
        else:
            raise error

    @bot.command(name="shop", help="Показывает вещи, которые вы можете купить")
    async def shop(ctx):
        embed = discord.Embed(title="Магазин", color=discord.Colour.gold())
        for item, price in store_items.items():
            embed.add_field(name=item, value=f"Цена: {price} монет", inline=False)
        embed.add_field(
            name="",
            value="**Чтобы купить предмет, введите !buy <нужный предмет>**",
            inline=False,
        )
        await ctx.send(embed=embed)

    @bot.command(name="buy", help="Купить предмет")
    async def buy(ctx, item_name: str):
        data = await load_data()
        user_id = str(ctx.author.id)
        if user_id not in data:
            data[user_id] = {"balance": 0, "properties": []}
        balance = data[user_id]["balance"]

        if item_name in store_items:
            item_cost = store_items[item_name]
            if balance >= item_cost:
                balance -= item_cost
                data[user_id]["balance"] = balance
                await save_data(data)
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

    @bot.command(
        name="property_list", help="Показать доступные для покупки недвижимости"
    )
    async def property_list(ctx):
        embed = discord.Embed(title="Недвижимость", color=discord.Colour.green())
        for property, details in properties.items():
            embed.add_field(
                name=property,
                value=f"Цена: {details['cost']} монет, Доход: {details['income']} монет в день",
                inline=False,
            )
        await ctx.send(embed=embed)

    @bot.command(name="buy_property", help="Купить недвижимость")
    async def buy_property(ctx, property_name: str):
        data = await load_data()
        user_id = str(ctx.author.id)
        if user_id not in data:
            data[user_id] = {"balance": 0, "properties": []}
        balance = data[user_id]["balance"]

        if property_name in properties:
            property_cost = properties[property_name]["cost"]
            if balance >= property_cost:
                balance -= property_cost
                data[user_id]["balance"] = balance
                if "properties" not in data[user_id]:
                    data[user_id]["properties"] = []
                data[user_id]["properties"].append(property_name)
                await save_data(data)
                await ctx.send(
                    f"{ctx.author.mention}, вы успешно купили {property_name} за {property_cost} монет."
                )
            else:
                await ctx.send(
                    f"{ctx.author.mention}, недостаточно средств для покупки {property_name}."
                )
        else:
            await ctx.send(
                f"{ctx.author.mention}, недвижимость {property_name} не найдена."
            )

    @bot.command(name="properties", help="Показать вашу недвижимость")
    async def properties_command(ctx):
        data = await load_data()
        user_id = str(ctx.author.id)
        if (
            user_id not in data
            or "properties" not in data[user_id]
            or not data[user_id]["properties"]
        ):
            await ctx.send(f"{ctx.author.mention}, у вас нет недвижимости.")
        else:
            properties_list = data[user_id]["properties"]
            embed = discord.Embed(
                title="Ваша недвижимость", color=discord.Colour.green()
            )
            for property in properties_list:
                embed.add_field(
                    name=property,
                    value=f"Доход: {properties[property]['income']} монет в день",
                    inline=False,
                )
            await ctx.send(embed=embed)

    @bot.command(name="guess", help="Угадай число от 1 до 10")
    @cooldown(1, 60, BucketType.user)
    async def guess_number(ctx):
        number = random.randint(1, 10)
        await ctx.send(
            f"{ctx.author.mention}, я загадал число от 1 до 10. У тебя есть 3 попытки угадать его!"
        )

        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and m.content.isdigit()
            )

        for i in range(3):
            try:
                guess = await bot.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                return await ctx.send(
                    f"{ctx.author.mention}, время вышло! Я загадал число {number}."
                )

            if int(guess.content) == number:
                data = await load_data()
                user_id = str(ctx.author.id)
                if user_id not in data:
                    data[user_id] = {"balance": 0, "properties": []}
                data[user_id]["balance"] += 50
                await save_data(data)
                return await ctx.send(
                    f"{ctx.author.mention}, поздравляю! Ты угадал число {number} и выиграл 50 монет!"
                )
            else:
                await ctx.send(f"{ctx.author.mention}, неправильно. Попробуй еще раз!")

        await ctx.send(
            f"{ctx.author.mention}, у тебя закончились попытки. Я загадал число {number}."
        )

    @guess_number.error
    async def guess_number_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"{ctx.author.mention}, вы можете использовать эту команду только раз в минуту."
            )
        else:
            raise error

    @tasks.loop(hours=24)
    async def daily_income():
        data = await load_data()
        for user_id, user_data in data.items():
            if isinstance(user_data, dict) and "properties" in user_data:
                daily_income = sum(
                    properties[prop]["income"] for prop in user_data["properties"]
                )
                user_data["balance"] += daily_income
        await save_data(data)
