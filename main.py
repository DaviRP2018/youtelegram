import json
import logging
import subprocess
from datetime import datetime, date
from time import sleep

import telebot
from pytube import YouTube
from telebot.types import Message


def log(message: str, level: str = "info") -> None:
    """
    Levels of Log Message
    There are two built-in levels of the log message.
    Debug : These are used to give Detailed information, typically of interest only when diagnosing problems.
    Info : These are used to Confirm that things are working as expected
    Warning : These are used an indication that something unexpected happened, or indicative of some problem in the near
    future
    Error : This tells that due to a more serious problem, the software has not been able to perform some function
    Critical : This tells serious error, indicating that the program itself may be unable to continue running
    :param message:
    :param level:
    :rtype: None
    :return:
    """
    message = "{} ==|=====> {}".format(datetime.now().time(), message)
    filename = "logs/log - %s.log" % date.today()
    logging.basicConfig(filename=filename, format="%(asctime)s - %(levelname)s: %(message)s", filemode="w")
    print(message)
    logger = logging.getLogger()
    if level == "info":
        logger.setLevel(logging.INFO)
        logger.info(message)
    elif level == "debug":
        logger.setLevel(logging.DEBUG)
        logger.debug(message)
    elif level == "warning":
        logger.setLevel(logging.WARNING)
        logger.warning(message)
    elif level == "error":
        logger.setLevel(logging.ERROR)
        logger.error(message)
    elif level == "critical":
        logger.setLevel(logging.CRITICAL)
        logger.critical(message)


TOKEN = "1706208033:AAGp3FOWnZWWivPVIJ3Tn1FKuSRqouGxYKs"
SAVE_PATH = "tmp/"


def manage_user(message: Message) -> None:
    log(message.from_user.first_name)
    with open("users.json", "r") as users_json:
        data = users_json.read()
    users = json.loads(data)

    if message.from_user.first_name not in users:
        users[message.from_user.first_name] = message.from_user.id
        with open("users.json", "w") as users_json:
            users_json.write(json.dumps(users))


def clean() -> None:
    log("Cleaning tmp folder")
    process = subprocess.Popen("rm -rf tmp/*".split(), stdout=subprocess.PIPE)
    output, err = process.communicate()
    log(str(output))
    log(str(err), "error")


def main() -> None:
    try:
        bot = telebot.TeleBot(TOKEN, parse_mode=None)

        @bot.message_handler(commands=["start", "help"])
        def send_welcome(message: Message) -> None:
            bot.reply_to(
                message, "Bem vindo! Me mande o link do vídeo e eu vou tentar baixar para você."
            )

        @bot.message_handler(func=lambda m: True, content_types=["text"])
        def reply_to_user(message: Message) -> None:
            manage_user(message)

            link = message.text

            msg = "Link válido, aguarde."
            bot.send_message(message.from_user.id, msg)
            log(msg)
            try:
                # object creation using YouTube
                # which was imported in the beginning
                yt = YouTube(link)
                filename = f"{yt.title}.mp4"
                try:
                    audio = open(f"{SAVE_PATH}{filename}", "rb")
                    bot.send_audio(message.chat.id, audio)
                    log("Audio sent.")
                    msg = "Tá aqui o que você quer"
                    bot.send_message(message.from_user.id, msg)
                    log(msg)
                    return
                except Exception as err:
                    log(str(err), "error")
            except Exception as err:
                log(str(err), "error")
                bot.send_message(message.from_user.id, "Erro de conexão, por favor tente novamente mais tarde.")
            else:
                bot.send_message(message.from_user.id, "conexão estabelecida.")
                try:
                    bot.send_message(message.from_user.id, "Baixando seu vídeo...")
                    yt.streams.filter(type="audio").first().download(SAVE_PATH, filename)
                except Exception as err:
                    log(str(err), "error")
                    bot.send_message(message.from_user.id, "Error")
                else:
                    audio = open(f"{SAVE_PATH}{filename}", "rb")
                    bot.send_message(message.from_user.id, "Tá aqui o que você quer:")
                    bot.send_audio(message.chat.id, audio)
            finally:
                clean()

        log("Starting bot...")
        bot.polling(none_stop=False, interval=0, timeout=20)
        log("Bot started...")

    except AssertionError as err:
        log(str(err), "error")
    except Exception as err:
        log(str(err), "error")


if __name__ == "__main__":
    # while True -> pq o bot fica parando sozinho por conta de eu nao ser donator ou algo assim
    retries = 0
    while retries < 10:
        main()
        sleep(15)
        retries += 1
