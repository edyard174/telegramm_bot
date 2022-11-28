import requests
import datetime
import logging
import os
import random
import re
from bs4 import BeautifulSoup as b
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import BotDB


logging.basicConfig(level=logging.INFO)

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

BotDB = BotDB('account.db')

know = InlineKeyboardMarkup(row_width=1)
b5 = InlineKeyboardButton(text='Курс криптовалют', callback_data='da')
b1 = InlineKeyboardButton(text='Бугалтер', callback_data='gf')
know.add(b5, b1)

kpih = InlineKeyboardMarkup(row_width=1)
b6 = InlineKeyboardButton(text='Биткоин', callback_data='btc')
b7 = InlineKeyboardButton(text='Эфириум', callback_data='eth')
kpih.add(b6, b7)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)
    sti = open('Sticker_2.tgs', 'rb')
    await bot.send_sticker(message.chat.id, sti)
    await bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}', reply_markup=know)


@dp.message_handler(commands=("spent", "earned", "s", "e"), commands_prefix="/!")
async def start_1(message: types.Message):
    cmd_variants = (('/spent', '/s', '!spent', '!s'), ('/earned', '/e', '!earned', '!e'))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

    value = message.text
    for i in cmd_variants:
        for j in i:
            value = value.replace(j, '').strip()

    if (len(value)):
        x = re.findall(r"\d+(?:.\d+)?", value)
        if (len(x)):
            value = float(x[0].replace(',', '.'))

            BotDB.add_record(message.from_user.id, operation, value)

            if (operation == '-'):
                await message.reply("✅ Запись о расходе успешно внесена!")
            else:
                await message.reply("✅ Запись о доходе успешно внесена!")
        else:
            await message.reply("Не удалось определить сумму!")
    else:
        await message.reply("Не введена сумма!")


@dp.message_handler(commands=("history", "h"), commands_prefix="/!")
async def start_2(message: types.Message):
    cmd_variants = ('/history', '/h', '!history', '!h')
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }
    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()
    within = 'day'
    if (len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if (als == cmd):
                    within = k
    records = BotDB.get_records(message.from_user.id, within)
    if (len(records)):
        answer = f"🕘 История операций за {within_als[within][-1]}\n\n"
        for r in records:
            answer += "➖ Расход" if not r[2] else "➕ Доход"
            answer += f" - {r[3]}" + " Рублей "
            answer += f"({r[4]})\n"
        await message.reply(answer)
    else:
        await message.reply("Записей не обнаружено!")


@dp.callback_query_handler(text='gf')
async def bygalter(callback: types.CallbackQuery):
    await callback.answer('Смотри чё покажу')
    await callback.message.answer('''Чтоб записать "➕Доход➕" "➖Расход➖" напиши Расход или Доход и через 
									пробел пишешь сумму''', reply_markup=kpih)


@dp.callback_query_handler(text='da')
async def get_info_cripto(callback: types.CallbackQuery):
    await callback.answer('Ща позырим')
    await callback.message.answer('Выбири крипту', reply_markup=kpih)


@dp.callback_query_handler(text='btc')
async def btc(callback: types.CallbackQuery):
    await callback.answer('Вот')
    resp = requests.get(url="https://yobit.net/api/3/ticker/btc_usd?ignore_invalid=1")
    data = resp.json()
    price = data['btc_usd']['avg']
    await callback.message.answer('BTC=' + str(int(price)) + '\U0001f4b2')


@dp.callback_query_handler(text='eth')
async def eth(callback: types.CallbackQuery):
    await callback.answer('Вот')
    resp_2 = requests.get(url="https://yobit.net/api/3/ticker/eth_usd?ignore_invalid=1")
    data_2 = resp_2.json()
    price_2 = data_2['eth_usd']['avg']
    await callback.message.answer('ETH=' + str(int(price_2)) + '\U0001f4b2')


@dp.message_handler(lambda message: 'курс' in message.text.lower())
async def get_kyrs(message: types.Message):
    try:
        ret = message.text.lower()[5::]
        kap = message.text.upper()[5::]
        kyrs = requests.get(url=f"https://yobit.net/api/3/ticker/{ret}_usd?ignore_invalid=1")
        dait = kyrs.json()
        seg = f"{ret}_usd"
        await message.answer(f'\U00002705 Курс {kap}=' + str(int(dait[seg]['avg'])) + '\U0001f4b2')
    except:
        await message.reply("\U0000274C Проверь название крипты \U0000274C")


@dp.message_handler(lambda message: 'погода' in message.text.lower())
async def get_weather(message: types.Message):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text[7::]}&appid={open_weather_token}&units=metric")
        data = r.json()
        city = data['name']
        temp_city = data['main']['temp']
        vlaga = data['main']['humidity']
        davlenie = data['main']['pressure']
        veter = data['wind']['speed']
        rasvet = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        zakat = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        den = datetime.datetime.fromtimestamp(data['sys']['sunset']) - datetime.datetime.fromtimestamp(
            data['sys']['sunrise'])

        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                            f"Погода в городе: {city}\n"
                            f"Средняя Температура: {int(temp_city)} ℃\n"
                            f"Влажность: {vlaga}\n"
                            f"Давление: {davlenie} мПа\n"
                            f"Ветер: {veter} м/с\n"
                            f"Восход солнца: {str(rasvet)[11:-3:]}\n"
                            f"Закат: {str(zakat)[11:-3:]}\n"
                            f"Продолжительность дня: {den}"
                            )

    except:
        await message.reply("\U00002620 Проверте название города \U00002620")


@dp.message_handler(lambda message: 'анекдот' in message.text.lower())
async def anecdot(message: types.Message):
    url = "https://www.nekdo.ru/"
    r = requests.get(url)
    s = b(r.text, 'html.parser')
    anecdots = s.find_all('div', class_='text')
    cls_anecdot = [c.text for c in anecdots]
    rod = cls_anecdot[random.randint(0, len(cls_anecdot))]
    await message.reply(f"{rod} \U0001F923")


if __name__ == '__main__':
    executor.start_polling(dp)
