import json
import logging
from time import sleep

import telebot
from pytube import YouTube
from telebot.types import Message

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


TOKEN = "1706208033:AAGp3FOWnZWWivPVIJ3Tn1FKuSRqouGxYKs"
SAVE_PATH = "tmp/"


def manage_user(message: Message) -> None:
    logger.info(message.from_user.first_name)
    with open("users.json", "r") as users_json:
        data = users_json.read()
    users = json.loads(data)

    if message.from_user.first_name not in users:
        users[message.from_user.first_name] = message.from_user.id
        with open("users.json", "w") as users_json:
            users_json.write(json.dumps(users))


def validate_link(link: str) -> bool:
    if all([link.startswith("https://"), link.find("youtube.com") != -1]):
        return True
    return False


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

            if not validate_link(link):
                bot.send_message(message.from_user.id, "Link inválido.")
                return

            bot.send_message(message.from_user.id, "Link válido, aguarde.")
            try:
                # object creation using YouTube
                # which was imported in the beginning
                yt = YouTube(link)
                filename = f"{yt.title}.mp4"
                try:
                    audio = open(f"{SAVE_PATH}{filename}", "rb")
                    bot.send_message(message.from_user.id, "Tá aqui o que você quer:")
                    bot.send_audio(message.chat.id, audio)
                    return
                except Exception as err:
                    logger.error(err)
            except Exception as err:
                logger.error(err)
                bot.send_message(message.from_user.id, "Erro de conexão, por favor tente novamente mais tarde.")
            else:
                bot.send_message(message.from_user.id, "conexão estabelecida.")
                try:
                    bot.send_message(message.from_user.id, "Baixando seu vídeo...")
                    yt.streams.filter(type="audio").first().download(SAVE_PATH, filename)
                except Exception as err:
                    logger.error(err)
                    bot.send_message(message.from_user.id, "Error")
                else:
                    audio = open(f"{SAVE_PATH}{filename}", "rb")
                    bot.send_message(message.from_user.id, "Tá aqui o que você quer:")
                    bot.send_audio(message.chat.id, audio)

        logger.info("Starting bot...")
        bot.polling(none_stop=False, interval=0, timeout=20)
        logger.info("Bot started...")

    except AssertionError as err:
        logger.error(err)
    except Exception as err:
        logger.error(err)


if __name__ == "__main__":
    # while True -> pq o bot fica parando sozinho por conta de eu nao ser donator ou algo assim
    retries = 0
    while retries < 10:
        main()
        sleep(15)
        retries += 1
