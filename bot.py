import music_rec
import telebot
import os
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
    filename_usr_audio = directory + "USR" + downloadtime + ".ogg"

    with open(filename_usr_audio, "wb") as f:
        f.write(data)

    # doing something
    filename_bot_txt = directory + "TXT" + downloadtime + ".txt"
    music_rec.wav2txt(src_file=filename_usr_audio, dst_file=filename_bot_txt)

    with open(filename_bot_txt, "r") as txt_file:
        notes = txt_file.readline()

    # answer user
    bot.send_message(user, "А вот и ваши ноты \n" + notes)

    filename_bot_audio = directory + "BOT" + downloadtime + ".opus"
    music_rec.txt2wav(src_file=filename_bot_txt, dst_file=filename_bot_audio, duration=0.2)
    
    with open(filename_bot_audio, 'rb') as audio_bot:
        data_bot = audio_bot.read()
        print(data_bot)
        ret_msg = bot.send_voice(user, data_bot)
        print(ret_msg)



bot.polling(none_stop=True, interval=0)

