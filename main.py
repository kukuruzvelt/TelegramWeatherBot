from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from WeatherProvider import WeatherioProvider
import enum

from token import Consts

STATE = None
WEATHER_PROVIDER = None

CITY = 1
LANGUAGE = 2
TOWN = None  # временно заменяет Запрос к БД
LANG = 'en'  # временно заменяет Запрос к БД


@enum.unique
class Languages(enum.Enum):  # временно заменяет БД
    en = 1
    ru = 2
    ua = 3

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))


def start(update, context):
    pass


# function to handle the /help command
def help(update, context):
    update.message.reply_text('help command received')


# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text('an error occured')


# function to handle normal text
def text(update, context):
    global STATE
    if STATE == CITY:
        return setCity(update, context)
    else:
        update.message.reply_text("I don't know this command")


def callback(update, context):
    global LANG
    global STATE

    query = update.callback_query
    query.answer()

    if query.data == 'setLanguage':
        setLanguage(update, context)
    elif query.data == 'setWeatherParams':
        setWeatherParams(update, context)
    elif query.data == 'setCity':
        getCityInfo(update, context)

    elif STATE == LANGUAGE:
        LANG = query.data
        query.edit_message_text(text=f"Selected language: {query.data}")
        STATE = None


def settings(update, context):
    keyboard = [
        [InlineKeyboardButton('Language settings', callback_data='setLanguage')],
        [InlineKeyboardButton('Setting weather parameters', callback_data='setWeatherParams')],
        [InlineKeyboardButton('City setting', callback_data='setCity')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = 'Choose what you want to customize'
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)


def getCityInfo(update, context):
    global STATE
    STATE = CITY
    update.callback_query.message.reply_text("Enter the city for which you want to get the weather.")


def setLanguage(update, context):
    global STATE
    STATE = LANGUAGE
    keyboard = [
        [InlineKeyboardButton('Русский', callback_data='ru')],
        [InlineKeyboardButton('English', callback_data='en')],
        [InlineKeyboardButton('Українська', callback_data='uk')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = 'Choose language'
    update.callback_query.message.reply_text(message_reply_text, reply_markup=reply_markup)


def setCity(update, context):
    # todo здесь мы проверяем, что можем получить погоду для заданного города, и если да, то сохраняем это значение /
    #  в БД вместе с id чата

    # id = {update.message.user.id}
    global TOWN
    global STATE
    TOWN = update.message.text
    if WeatherioProvider.isOK(TOWN):
        update.message.reply_text(f"I got data about the city, city = {TOWN}")
        STATE = None
    else:
        TOWN = None
        update.message.reply_text("Wrong city, try again")


def setWeatherParams(update, context):
    pass


def current(update, context):
    global TOWN
    update.message.reply_text(f'{WEATHER_PROVIDER.getCurrent(TOWN, LANG)}')


def forecast(update, context):
    pass


def subscription(update, context):
    pass


def advice(update, context):
    pass


def main():
    token = Consts.TOKEN

    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    global WEATHER_PROVIDER
    WEATHER_PROVIDER = WeatherioProvider

    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("settings", settings))
    dispatcher.add_handler(CommandHandler("current", current))
    dispatcher.add_handler(CommandHandler("forecast", forecast))
    dispatcher.add_handler(CommandHandler("subscription", subscription))
    dispatcher.add_handler(CommandHandler("advice", advice))

    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    dispatcher.add_handler(CallbackQueryHandler(callback))

    # add an handler for errors
    dispatcher.add_error_handler(error)

    # start your shiny new bot
    updater.start_polling()

    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
