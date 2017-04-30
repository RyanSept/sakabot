from slackbot.bot import Bot
import logging


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    logging.basicConfig()
    main()
