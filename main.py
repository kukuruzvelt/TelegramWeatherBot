from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from Languages import Languages
from DAO import DAO
from WeatherProvider import WeatherioProvider, WeatherProvider
import re

WEATHER_PROVIDER = WeatherProvider


def start(update, context):
    user_id = update.message.chat.id
    context.job_queue.run_repeating(callback_minute, interval=59, first=1,
                                    context=update.message.chat_id)
    lang = DAO.get_language(update.message.chat.id)
    if not DAO.is_in_db(user_id):
        DAO.create_new_user(user_id)
        update.message.reply_text(Languages.get_message("start_new", lang, update.message.chat.first_name))
    else:
        update.message.reply_text(Languages.get_message("start_old", lang, update.message.chat.first_name))


def callback_minute(context):
    chat_id = context.job.context
    current_time = datetime.now().strftime("%H:%M")
    if chat_id in DAO.get_users_subscribe_for_time(current_time):
        town = DAO.get_city(chat_id)
        lang = DAO.get_language(chat_id)
        params = DAO.get_params(chat_id)
        try:
            context.bot.send_message(chat_id=chat_id,
                                     text=f'{WEATHER_PROVIDER.getCurrent(town, lang, params)}')

        except TypeError as e:
            context.bot.send_message(chat_id=chat_id,
                                     text=Languages.get_message("what_city", lang))


# function to handle the /help command
def help(update, context):
    # print(DAO.get_language(update.message.chat.id))
    update.message.reply_text(Languages.get_message("help", DAO.get_language(update.message.chat.id)))


# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text(Languages.get_message("error", DAO.get_language(update.message.chat.id)))


# function to handle normal text
def text(update, context):
    if DAO.get_action(update.message.chat.id) == "CITY":
        return setCity(update, context)
    elif DAO.get_action(update.message.chat.id) == "TIME-SLOTS":
        return setSubscription(update, context)
    else:
        update.message.reply_text(Languages.get_message("text", DAO.get_language(update.message.chat.id)))


def callback(update, context):
    lang = DAO.get_language(update.callback_query.message.chat.id)
    query = update.callback_query
    query.answer()

    if query.data == 'setLanguage':
        setLanguage(update, context)
    elif query.data == 'setWeatherParams':
        setWeatherParams(update, context)
    elif query.data == 'setCity':
        getCityInfo(update, context)

    elif DAO.get_action(query.message.chat.id) == "LANGUAGE":
        DAO.set_language(query.message.chat.id, query.data)
        query.edit_message_text(text=Languages.get_message("callback_lang", lang, query.data))
        DAO.set_action(query.message.chat.id, None)

    elif DAO.get_action(query.message.chat.id) == 'TIME-SLOTS':
        if query.data == 'create_subscription':
            getSubscriptionInfo(update, context)
        elif query.data == 'view_subscriptions':
            getSubscriptions(update, context)
        elif query.data == 'del_subscription':
            delSubscription(update, context)
        elif query.data == "submit":
            DAO.set_action(query.message.chat.id, None)
            update.callback_query.edit_message_text(Languages.get_message("callback_time_slots", lang))
        else:
            DAO.del_subscription(query.message.chat.id, query.data)
            delSubscription(update, context)

    elif DAO.get_action(query.message.chat.id) == "PARAMS":
        current_params = DAO.get_params(query.message.chat.id)

        if query.data == "hum":
            changed_params = [not current_params[0], current_params[1], current_params[2]
                , current_params[3], current_params[4], current_params[5]]
            DAO.set_params(query.message.chat.id, changed_params)
            setWeatherParams(update, context)

        elif query.data == "temp":
            changed_params = [current_params[0], not current_params[1], current_params[2]
                , current_params[3], current_params[4], current_params[5]]
            DAO.set_params(query.message.chat.id, changed_params)
            setWeatherParams(update, context)

        elif query.data == "f_l_temp":
            changed_params = [current_params[0], current_params[1], not current_params[2]
                , current_params[3], current_params[4], current_params[5]]
            DAO.set_params(query.message.chat.id, changed_params)
            setWeatherParams(update, context)

        elif query.data == "w_s":
            changed_params = [current_params[0], current_params[1], current_params[2]
                , not current_params[3], current_params[4], current_params[5]]
            DAO.set_params(query.message.chat.id, changed_params)
            setWeatherParams(update, context)

        elif query.data == "pres":
            changed_params = [current_params[0], current_params[1], current_params[2]
                , current_params[3], not current_params[4], current_params[5]]
            DAO.set_params(query.message.chat.id, changed_params)
            setWeatherParams(update, context)

        elif query.data == "desc":
            changed_params = [current_params[0], current_params[1], current_params[2]
                , current_params[3], current_params[4], not current_params[5]]
            DAO.set_params(query.message.chat.id, changed_params)
            setWeatherParams(update, context)

        elif query.data == "submit":
            DAO.set_action(query.message.chat.id, None)
            update.callback_query.edit_message_text(Languages.get_message("callback_params", lang))


def getSubscriptionInfo(update, context):
    lang = DAO.get_language(update.callback_query.message.chat.id)
    update.callback_query.message.reply_text(Languages.get_message("getSubscriptionInfo", lang))


def getSubscriptions(update, context):
    times = DAO.get_subscriptions(update.callback_query.message.chat.id)
    lang = DAO.get_language(update.callback_query.message.chat.id)
    result = Languages.get_message("getSubscriptions", lang)
    for i in times:
        result += f"\n {i}"
    update.callback_query.edit_message_text(result)


def setSubscription(update, context):
    time = update.message.text
    lang = DAO.get_language(update.message.chat.id)
    if re.match("^([0-1]?[0-9]|2[0-3])(?::([0-5]?[0-9]))$", time):
        try:
            DAO.create_subscription(update.message.chat.id, time, lang)
            update.message.reply_text(Languages.get_message("setSubscription_create", lang, time))
            DAO.set_action(update.message.chat.id, None)
        except TypeError as e:
            update.message.reply_text(e.__str__())
            DAO.set_action(update.message.chat.id, None)
        except ValueError as e:
            update.message.reply_text(e.__str__())
    else:
        update.message.reply_text(Languages.get_message("setSubscription", lang))


def delSubscription(update, context):
    lang = DAO.get_language(update.callback_query.message.chat.id)
    reply_markup = InlineKeyboardMarkup(__create_subscription_keyboard(DAO.get_subscriptions
                                                                       (update.callback_query.message.chat.id), lang))
    message_reply_text = Languages.get_message("delSubscription", lang)
    update.callback_query.edit_message_text(message_reply_text, reply_markup=reply_markup)


def __create_subscription_keyboard(params, lang):
    keyboard = []
    for i in params:
        keyboard.append([InlineKeyboardButton(i, callback_data=i)])
    keyboard.append([InlineKeyboardButton(Languages.get_message("submit", lang), callback_data='submit')])
    return keyboard


def setWeatherParams(update, context):
    lang = DAO.get_language(update.callback_query.message.chat.id)
    DAO.set_action(update.callback_query.message.chat.id, "PARAMS")
    reply_markup = InlineKeyboardMarkup(__create_params_keyboard(DAO.get_params(update.callback_query.message.chat.id), lang))
    message_reply_text = Languages.get_message("setWeatherParams", lang)
    update.callback_query.edit_message_text(message_reply_text, reply_markup=reply_markup)


def __create_params_keyboard(params, lang):
    names = Languages.get_message("create_params_keyboard", lang)
    for i in range(0, 6):
        if params[i]:
            names[i] += " ✓"
    keyboard = [
        [InlineKeyboardButton(names[0], callback_data='hum')],
        [InlineKeyboardButton(names[1], callback_data='temp')],
        [InlineKeyboardButton(names[2], callback_data='f_l_temp')],
        [InlineKeyboardButton(names[3], callback_data='w_s')],
        [InlineKeyboardButton(names[4], callback_data='pres')],
        [InlineKeyboardButton(names[5], callback_data='desc')],
        [InlineKeyboardButton(Languages.get_message("submit", lang), callback_data='submit')]
    ]
    return keyboard


def settings(update, context):
    lang = DAO.get_language(update.message.chat.id)
    keyboard = [
        [InlineKeyboardButton(Languages.get_message("settings_language", lang), callback_data='setLanguage')],
        [InlineKeyboardButton(Languages.get_message("settings_weather_param", lang), callback_data='setWeatherParams')],
        [InlineKeyboardButton(Languages.get_message("settings_city", lang), callback_data='setCity')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = Languages.get_message("choose", lang)
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)


def getCityInfo(update, context):
    DAO.set_action(update.callback_query.message.chat.id, "CITY")
    lang = DAO.get_language(update.callback_query.message.chat.id)
    update.callback_query.edit_message_text(Languages.get_message("getCityInfo", lang))


def setLanguage(update, context):
    DAO.set_action(update.callback_query.message.chat.id, "LANGUAGE")
    keyboard = [
        [InlineKeyboardButton('Русский', callback_data='ru')],
        [InlineKeyboardButton('English', callback_data='en')],
        [InlineKeyboardButton('Українська', callback_data='uk')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    lang = DAO.get_language(update.callback_query.message.chat.id)
    message_reply_text = Languages.get_message("setLanguage", lang)
    update.callback_query.edit_message_text(message_reply_text, reply_markup=reply_markup)


def setCity(update, context):
    town = update.message.text
    lang = DAO.get_language(update.message.chat.id)
    if WeatherioProvider.isOK(town):
        DAO.set_city(update.message.chat.id, town)
        update.message.reply_text(Languages.get_message("setCity_create", lang, town))
        DAO.set_action(update.message.chat.id, None)
    else:
        update.message.reply_text(Languages.get_message("setCity", lang))


def current(update, context):
    town = DAO.get_city(update.message.chat.id)
    lang = DAO.get_language(update.message.chat.id)
    params = DAO.get_params(update.message.chat.id)
    try:
        update.message.reply_text(f'{WEATHER_PROVIDER.getCurrent(town, lang, params)}')
    except TypeError as e:
        print(e)
        lang = DAO.get_language(update.message.chat.id)
        update.message.reply_text(Languages.get_message("what_city", lang))


def forecast(update, context):
    town = DAO.get_city(update.message.chat.id)
    lang = DAO.get_language(update.message.chat.id)
    params = DAO.get_params(update.message.chat.id)
    try:
        update.message.reply_text(f'{WEATHER_PROVIDER.getForecast(town, lang, params)}')
    except TypeError as e:
        lang = DAO.get_language(update.message.chat.id)
        update.message.reply_text(Languages.get_message("what_city", lang))


def subscription(update, context):
    lang = DAO.get_language(update.message.chat.id)
    DAO.set_action(update.message.chat.id, "TIME-SLOTS")
    keyboard = [
        [InlineKeyboardButton(Languages.get_message("subscription_new", lang), callback_data='create_subscription')],
        [InlineKeyboardButton(Languages.get_message("subscription_view", lang), callback_data='view_subscriptions')],
        [InlineKeyboardButton(Languages.get_message("subscription_del", lang), callback_data='del_subscription')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_reply_text = Languages.get_message("choose", lang)
    update.message.reply_text(message_reply_text, reply_markup=reply_markup)
    # getSubscriptionInfo(update, context)


def advice(update, context):
    town = DAO.get_city(update.message.chat.id)
    lang = DAO.get_language(update.message.chat.id)
    try:
        update.message.reply_text(f'{WEATHER_PROVIDER.getAdvice(town, lang)}')
    except TypeError as e:
        print(e)
        lang = DAO.get_language(update.message.chat.id)
        update.message.reply_text(Languages.get_message("what_city", lang))


def main():
    TOKEN = "2145526807:AAGaUQ7B3oFBuxa1QF4DluP9jO_LM7T4CWU"

    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
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
