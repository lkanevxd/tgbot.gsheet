import config
import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import *

from loguru import logger

from googlesheet_table import GoogleTable


logger.add(
    config.bot_settings["LOG_FILE"],
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="1 week",
    compression="zip",
)

class ZaryaTelegramBot(Bot):
  def __init__(
    self,
    token,
    parse_mode,
    google_table=None
  ):
    super().__init__(token, parse_mode = parse_mode)
    self._google_table: GoogleTable = google_table

bot = ZaryaTelegramBot(
  token=config.bot_settings["TOKEN"],
  parse_mode=types.ParseMode.HTML,
  google_table=GoogleTable("creds.json",
                          "https://docs.google.com/spreadsheets/d/1aMXNvGL4qx4mS8TrYVBPIlk-4WUUiM9bjvsce3bs-eU/edit#gid=0"),
)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def cheers(message: types.Message):
  await message.answer('(^_^) привет! введи данные человека, информацию о котором ты хочешь найти')

@dp.message_handler(commands=['restart'])
async def restart(message: types.Message):
  await message.answer('(n_n) все по той же схеме! введи данные человека, информацию о котором ты хочешь найти')

@dp.message_handler(commands=['new_employee'])
async def employee(message: types.Message):
  await message.answer('(-_o) вот форма для заполнения: https://forms.gle/zze7L4U1MYZ6m41L6')

# @dp.message_handler(commands=['get_my_id'])
# async def get_id(message: types.Message):
#   await message.answer(f'(-_o) вот твой айди: <code>{message.from_user.id}</code>')

@dp.message_handler(lambda message: message.text.lower().startswith('спасибо'))
async def say_thanks(message: types.Message):
  await message.answer_sticker(r'CAACAgIAAxkBAAJuHmSbZ_DI8XqNanwVspCKcZiPVcU6AAIQKQACxo1hSzuqU6Kksis0LwQ')

@dp.message_handler(chat_id=config.users_data['admin_id'], commands='dr')
async def birthday_reminder(message: types.Message):
  await types.ChatActions.typing()
  today = datetime.datetime.now().strftime('%d.%m')
  results: list[dict] = bot._google_table.search_user(today)
  if not results:
    try:
      await message.reply('(=_=) сегодня без др...')
    except Exception as send_error:
      logger.debug(f"{send_error}: trouble id: {id}")
      return

  else:
    message = '*(^o^)* день рождения у\n\n'
    for result in results:
      message += f'{result["name"]} {result["surname"]} {result["tg"]}\n{result["post"]}\n\n'
    for id in config.users_data['admin_id']:
      try:
        await bot.send_message(id, message)
      except Exception as send_error:
        logger.debug(f"{send_error}: trouble id: {id}")
        return

@dp.message_handler(lambda message: message.text.lower().startswith('эйчарам'))
async def hr(message: types.Message):
  await bot.send_message(-955995258, message["text"][7::])
  await message.answer('(^3^) твое сообщение успешно отправлено эйчарам!')

@dp.message_handler()
async def user_search(message: types.Message) -> None:
  if message.md_text == '/dr':
    try:
      await message.answer_sticker(r'CAACAgIAAxkBAAJ3kWSjTAjeuSZ_HaqOJugsp8ZFFp8NAAKFLAAC92ZhS4qAuAEeI_s8LwQ')
    except Exception as send_error:
      logger.debug(f"{send_error}: trouble id: {message.from_user.id}")
      return
    return

  try:
    await message.answer('(@_@) так, ща...')
  except Exception as send_error:
    logger.debug(f"{send_error}: trouble id: {message.from_user.id}")
    return

  await types.ChatActions.typing()
  user_id: str = str(message.from_id)
  searching_data: str = message.md_text.strip(' #/')
  results: list[dict] = bot._google_table.search_user(searching_data)
  if not results:
    try:
      await message.reply('(._.) этого человека нет в команде или ты неправильно ввел его данные!')
    except Exception as send_error:
      logger.debug(f"{send_error}: trouble id: {user_id}")
      return

  else:
    for result in results:
      try:
        await message.answer(
          f'🧿имя🧿\n{result["name"]} {result["surname"]}\n\n'
          f'🪬должность🪬\n{result["post"]}\n\n'
          f'💌почта💌\n{result["email"]}\n\n'
          f'✈️телега✈️\n{result["tg"]}\n\n'
          f'📱номер телефона📱\n+7{result["phone_num"][1:]}\n\n\n\n'
          )
      except Exception as send_error:
        logger.debug(f"{send_error}: trouble id: {user_id}")
        return
  try:
    await message.answer('(n_n) чтобы найти информацию о другом человеке, введи его данные')
  except Exception as send_error:
    logger.debug(f"{send_error}: trouble id: {user_id}")
    return


if __name__ == '__main__':
  executor.start_polling(dp, skip_updates=True)
