import logging
from data.UsersControl import SqlController
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import emoji

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

TOKEN = "6240755690:AAHlUlD1JoRzv3l7-SmgjcJZFRqWFNIyitE"

sqlCon = SqlController()

searching_keyboard = [[emoji.emojize(':thumbs_up:'), emoji.emojize(':thumbs_down:'), emoji.emojize(':ZZZ:')]]
searching_markup = ReplyKeyboardMarkup(searching_keyboard, one_time_keyboard=False, resize_keyboard=True)

main_keyboard = [['Профиль', emoji.emojize("Искать:rocket:")], [emoji.emojize('Кто меня лайкнул:red_heart:')]]
main_markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True, resize_keyboard=True)

gender_keyboard = [['male', 'female']]
gender_markup = ReplyKeyboardMarkup(gender_keyboard, one_time_keyboard=True, resize_keyboard=True)

profile_keyboard = [['Изменить профиль', 'Назад']]
profile_markup = ReplyKeyboardMarkup(profile_keyboard, one_time_keyboard=True, resize_keyboard=True)

change_profile_keyboard = [['Изменить имя', 'Изменить город', 'Изменить описание'], ['Удалить описание', 'Назад']]
change_profile_markup = ReplyKeyboardMarkup(change_profile_keyboard, one_time_keyboard=True, resize_keyboard=True)

rated_inline_keyboard = [[InlineKeyboardButton(emoji.emojize(':thumbs_up:'), callback_data='like'),
                          InlineKeyboardButton(emoji.emojize(':thumbs_down:'), callback_data="dislike")]]
rated_inline_markup = InlineKeyboardMarkup(rated_inline_keyboard)

skip_keyboard = [['Пропустить']]
skip_markup = ReplyKeyboardMarkup(skip_keyboard, one_time_keyboard=True, resize_keyboard=True)

back_keyboard = [['Назад']]
back_markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True, resize_keyboard=True)

isUserGetFirstRecomendation = False
firstResult = []
conv_handler = None
result_from_user = ()


async def send_my_profile(update, context):
    context.user_data['where_is_user'] = "profile"
    my_profile = sqlCon.Get_User_by_Chat_id(update.message.chat.id)
    text = ""
    if my_profile[6] != '':
        text = "Ты находишься в профиле.\n\n" \
               "Ты можешь изменить свой профиль или искать дальше!\n\n" + \
               emoji.emojize("Вот так выглядит твой профиль:backhand_index_pointing_down:\n\n") + \
               f"{my_profile[2]} - {my_profile[3]}, {my_profile[6]}"
    else:
        text = "Ты находишься в профиле.\n\n" \
               "Ты можешь изменить свой профиль или искать дальше!\n\n" + \
               emoji.emojize("Вот так выглядит твой профиль:backhand_index_pointing_down:\n\n") + \
               f"{my_profile[2]} - {my_profile[3]}"
    await update.message.reply_text(text, reply_markup=profile_markup)


async def echo(update, context):
    global isUserGetFirstRecomendation, firstResult, result_from_user
    msg = update.message.text
    if context.user_data['where_is_user'] == 'menu':
        if msg == emoji.emojize("Искать:rocket:"):
            isUserGetFirstRecomendation = True
            context.user_data['where_is_user'] = "searching"
            result = sqlCon.Find_User(update.message.chat.id)
            firstResult = result
            text = ""
            if result[6] != '':
                text = f"{result[2]} - {result[3]}, {result[6]}"
            else:
                text = f"{result[2]} - {result[3]}"
            await update.message.reply_text(text, reply_markup=searching_markup)
        if msg == emoji.emojize('Кто меня лайкнул:red_heart:'):
            users = sqlCon.Get_Rated_Users(sqlCon.Get_User_ID_By_Chat_ID(update.message.chat.id)[0])
            if len(users) == 0:
                await update.message.reply_text("Тебя еще никто не оценил.", reply_markup=main_markup)
            else:
                await update.message.reply_text("Вот кто тебя лайкнул:", reply_markup=main_markup)
            for ind, u in enumerate(users):
                user = u[0]
                text = ""
                if user[6] != '':
                    text = f"{user[2]} - {user[3]}, {user[6]}\n\nНенужные циферки - {user[0]}"
                else:
                    text = f"{user[2]} - {user[3]}\n\nНенужные циферки - {user[0]}"
                await update.message.reply_text(text, reply_markup=rated_inline_markup)
        if msg == "Профиль":
            await send_my_profile(update, context)
    elif context.user_data['where_is_user'] == "searching":
        if isUserGetFirstRecomendation:
            if msg == emoji.emojize(":thumbs_up:"):
                user_id = sqlCon.Get_User_ID_By_Chat_ID(update.message.chat.id)[0]
                await context.bot.send_message(chat_id=firstResult[1],
                                               text=f"Тебя лайкнули! Скорее посмотри.\n"
                                                    f"Чтобы посмотреть вернись в меню и нажми \"Кто меня лайкнул\"")
                sqlCon.Rate_User(firstResult[0], user_id)
                isUserGetFirstRecomendation = False
                firstResult = None
            elif msg == emoji.emojize(":thumbs_down:"):
                isUserGetFirstRecomendation = False
                firstResult = None
            elif msg == emoji.emojize(":ZZZ:"):
                isUserGetFirstRecomendation = False
                firstResult = None
                context.user_data["where_is_user"] = "menu"
                await update.message.reply_text("Ты в главном меню.\n\nВыбери один из вариантов:",
                                                reply_markup=main_markup)
        else:
            if msg == emoji.emojize(":thumbs_up:"):
                user_id = sqlCon.Get_User_ID_By_Chat_ID(update.message.chat.id)[0]
                await context.bot.send_message(chat_id=result_from_user[1],
                                               text=f"Тебя лайкнули! Скорее посмотри.\n"
                                                    f"Чтобы посмотреть вернись в меню и нажми \"Кто меня лайкнул\"")
                sqlCon.Rate_User(result_from_user[0], user_id)
            elif msg == emoji.emojize(":ZZZ:"):
                context.user_data["where_is_user"] = "menu"
                await update.message.reply_text("Ты в главном меню.\n\nВыбери один из вариантов:",
                                                reply_markup=main_markup)
        if msg == emoji.emojize(":thumbs_up:") or msg == emoji.emojize(":thumbs_down:"):
            result_from_user = sqlCon.Find_User(update.message.chat.id)
            text = ""
            if result_from_user[6] != '':
                text = f"{result_from_user[2]} - {result_from_user[3]}, {result_from_user[6]}"
            else:
                text = f"{result_from_user[2]} - {result_from_user[3]}"
            await update.message.reply_text(text, reply_markup=searching_markup)
    elif context.user_data['where_is_user'] == "profile":
        if msg == 'Изменить профиль':
            await update.message.reply_text("Ты находишься в изменении профиля!\n\n"
                                            "Выбери, что хочешь изменить или вернись в профиль:",
                                            reply_markup=change_profile_markup)
            context.user_data['where_is_user'] = "changing"
        elif msg == "Назад":
            context.user_data['where_is_user'] = "menu"
            await update.message.reply_text("Отлично! Давай начнем!", reply_markup=main_markup)
    elif context.user_data['where_is_user'] == 'changing':
        if msg == 'Изменить имя':
            context.user_data['where_is_user'] = "changing_name"
            await update.message.reply_text("Введи новое имя пользователя:", reply_markup=back_markup)
        elif msg == 'Изменить город':
            context.user_data['where_is_user'] = "changing_city"
            await update.message.reply_text("Введи новой город:", reply_markup=back_markup)
        elif msg == 'Изменить описание':
            context.user_data['where_is_user'] = "changing_description"
            await update.message.reply_text("Введи новое описание:", reply_markup=back_markup)
        elif msg == 'Удалить описание':
            sqlCon.Change_User_Description(update.message.chat.id, '')
            await send_my_profile(update, context)
        elif msg == 'Назад':
            await send_my_profile(update, context)
    elif context.user_data['where_is_user'] == "changing_name":
        if msg != 'Назад':
            sqlCon.Change_User_Name(update.message.chat.id, msg)
        await send_my_profile(update, context)
    elif context.user_data['where_is_user'] == "changing_city":
        if msg != 'Назад':
            sqlCon.Change_User_City(update.message.chat.id, msg)
        await send_my_profile(update, context)
    elif context.user_data['where_is_user'] == "changing_description":
        if msg != 'Назад':
            sqlCon.Change_User_Description(update.message.chat.id, msg)
        await send_my_profile(update, context)


async def check_inline_button(update, context):
    query = update.callback_query
    variant = query.data

    await query.answer()
    if variant == "like":
        id_of_user_in_database = query.message.text.split()[-1]
        user = sqlCon.Get_User_by_Id(id_of_user_in_database)
        await query.edit_message_text(text=f"Отлично! Вот алиас пользователя - {user[-1]}\n\n"
                                           "Кстати, вот его профиль:\n\n"
                                           f"{query.message.text}", reply_markup=InlineKeyboardMarkup([]))
    elif variant == "dislike":
        await query.edit_message_text(text=query.message.text, reply_markup=InlineKeyboardMarkup([]))


async def start(update, context):
    if sqlCon.is_user_was_here_before(update.message.chat.id) == 0:
        await update.message.reply_text(
            "Привет. Это дайвинчик 2.0!\n"
            "Для начала пользования введи свое имя:"
        )
        context.user_data['id'] = update.message.chat.id
        return 1
    else:
        context.user_data['where_is_user'] = 'menu'
        await update.message.reply_text(
            "Ты в главном меню.\n\nВыбери один из вариантов:", reply_markup=main_markup
        )
        return ConversationHandler.END


async def get_user_city(update, context):
    name = update.message.text
    context.user_data['name'] = name
    await update.message.reply_text(f"Теперь в каком городе ты живешь?")
    return 2


async def get_user_sex(update, context):
    city = update.message.text
    context.user_data['city'] = city
    await update.message.reply_text("Какого ты пола?", reply_markup=gender_markup)
    return 3


async def get_user_preference_by_sex(update, context):
    sex = update.message.text
    if sex != 'male' and sex != 'female':
        await update.message.reply_text("Нет такого варианта ответа", reply_markup=gender_markup)
        return 3
    else:
        context.user_data['sex'] = sex
        await update.message.reply_text("Кого ты хочешь найти?", reply_markup=gender_markup)
        return 4


async def get_user_description(update, context):
    pref_sex = update.message.text
    if pref_sex != 'male' and pref_sex != 'female':
        await update.message.reply_text("Нет такого варианта ответа", reply_markup=gender_markup)
        return 4
    else:
        context.user_data['pref_sex'] = pref_sex
        await update.message.reply_text("Расскажите что-то о себе", reply_markup=skip_markup)
        return 5


async def end_from_getting_data_from_user(update, context):
    if update.message.text == 'Пропустить':
        context.user_data['description'] = ''
    else:
        description = update.message.text
        context.user_data['description'] = description

    sqlCon.New_User(context.user_data['id'], context.user_data['name'], context.user_data['city'],
                    context.user_data['sex'], context.user_data['pref_sex'], context.user_data['description'],
                    f"@{update.message.chat.username}")

    context.user_data.clear()

    await update.message.reply_text("Отлично! Давай начнем!", reply_markup=main_markup)
    context.user_data['where_is_user'] = 'menu'

    return ConversationHandler.END


async def stop(update, context):
    pass
    # return ConversationHandler.END


def main():
    global conv_handler

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_city)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_sex)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_preference_by_sex)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_description)],
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, end_from_getting_data_from_user)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)

    text_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(text_handler)

    application.add_handler(CallbackQueryHandler(check_inline_button))

    application.run_polling()


if __name__ == '__main__':
    main()
