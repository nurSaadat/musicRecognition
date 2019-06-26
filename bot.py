import telebot
from datetime import datetime

# https://habr.com/ru/post/262247/

directory = "data/"
bot = telebot.TeleBot('894199518:AAE93CnLB4FNm1ZoxHi2_9-_jj9WgSFw5vc')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user = message.from_user.id
    text = message.text

    # log server
    print('Text request.')
    print('User: ' + str(user))
    print('Text: ' + text)

    # print user
    bot.send_message(user, "Пришли мне аудио сообщение, вместо текста: " + message.text)


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    user = message.from_user.id
    audio = message.voice

    # log server
    print('Voice request.')
    print('User: ' + str(user))
    print('Voice duration: ' + str(audio.duration))

    # print user
    bot.send_message(message.from_user.id, "Мне прислали аудио сообщение! Сейчас посмотрим, что там записано...")

    # save audio
    tele_file = bot.get_file(audio.file_id)
    data = bot.download_file(tele_file.file_path)
    downloadtime = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = directory + downloadtime + ".ogg"

    with open(filename, "wb") as f:
        f.write(data)

    # doing something

    # answer user
    bot.send_message(user, "Длина " + str(audio.duration))

bot.polling(none_stop=True, interval=0)

