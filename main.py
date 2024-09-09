import mysql.connector
import urllib.request
import requests
import asyncio
import dotenv
import time
import os

from asyncVK import Handler, Bot, run_polling
from asyncVK.dispatcher import Dispatcher
from threading import Thread
from pyowm import OWM
from PIL import Image

from keyboards import *

global registration_mode, ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode
global profile_name, profile_age, profile_city, profile_description, profile_gender
global bot_main_msg_id, photo_name, chat_user_platform, chat_user_platform_id
global stop_thread, new_msg_current_chat, current_bot_txt_img

dotenv.load_dotenv('../.env')
TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = int(os.getenv('VK_GROUP_ID'))

bot = Bot(token=TOKEN, group_id=GROUP_ID)
owm = OWM(os.getenv('OWM_TOKEN'))
mgr = owm.weather_manager()

conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user='root',
    passwd='',
    database='messages')
cur = conn.cursor()

registration_mode = CHAT_MODE = 0
current_bot_txt_img = ['', '']


async def upload_photo(photo2up):
    photo2up = f'../user_profile_photos/{photo2up}.jpg'
    try:
        step1 = await bot.execute(method="photos.getMessagesUploadServer")
        step2 = requests.post(step1['response']['upload_url'], files={'photo': open(f'{photo2up}', 'rb')}).json()
        step3 = await bot.execute(
            "photos.saveMessagesPhoto", photo=step2['photo'], server=step2['server'], hash=step2['hash'])
        result_photo = "photo{}_{}".format(step3['response'][0]["owner_id"], step3['response'][0]["id"])
        return result_photo
    except Exception as err:
        print('upload err\n', err)
        return None


async def edit_msg(keys):
    await bot.execute("messages.edit", message_id=f'{bot_main_msg_id[0]}', peer_id=bot_main_msg_id[1], keyboard=keys,
                      message=current_bot_txt_img[0], attachment=await upload_photo(current_bot_txt_img[1]))


@bot.handle
@Handler.on("message_reply")
async def msg_to_edit(dp: Dispatcher):
    global bot_main_msg_id
    bot_msg = dp.event.get('object')
    bot_main_msg_id = bot_msg.get('id'), bot_msg.get('peer_id')


@bot.handle
@Handler.on("message_new")
async def handler(dp: Dispatcher):
    global registration_mode, bot_main_msg_id, chat_user_platform, chat_user_platform_id, CHAT_MODE
    global stop_thread
    global current_bot_txt_img

    msg = dp.text

    if msg == 'start':
        registration_mode = CHAT_MODE = 0
        current_bot_txt_img = ['Меню', 'media']
        await dp.send_message(text=current_bot_txt_img[0], attachment=await upload_photo(current_bot_txt_img[1]),
                              keyboard=await main_menu_create(dp.user_id))

    elif msg == 'stop':
        stop_thread = True
        registration_mode = CHAT_MODE = 0
        current_bot_txt_img = ['Вы вышли из режима переписки', 'media']
        await dp.send_message(text=current_bot_txt_img[0], attachment=await upload_photo(current_bot_txt_img[1]),
                              keyboard=await main_menu_create(dp.user_id))

# ===========================================================================================================Регистрация
    elif registration_mode == 1:
        global ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode, photo_name
        global profile_name, profile_age, profile_city, profile_description

        if ch_name_mode == 1:
            global a
            var_name = msg.lower()
            for i in var_name:
                if i not in ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р',
                             'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', '-', ' ']:
                    a = 0
                    break
                else:
                    a = 1

            if a == 1:
                profile_name = var_name.title()
                ch_name_mode = 0
            else:
                current_bot_txt_img[0] = 'Введите имя кириллицей без цифр и специальных символов'
                await edit_msg(keys=await profile_edit_kb())
                await asyncio.sleep(1.5)
                current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
                await edit_msg(keys=await profile_edit_kb())

        elif ch_age_mode == 1:
            var_age = msg
            try:
                var_age = int(var_age)
                if var_age >= 18:
                    if var_age < 125:
                        profile_age = var_age
                        ch_age_mode = 0
                    else:
                        current_bot_txt_img[0] = 'Напишите ваш реальный возраст'
                        await edit_msg(keys=await profile_edit_kb())
                        await asyncio.sleep(1.5)
                        current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
                        await edit_msg(keys=await profile_edit_kb())
                else:
                    await dp.send_message(text='Сервис предназанчен для лиц страше 18 лет')

            except Exception as err:
                print('int age\n', err)
                current_bot_txt_img[0] = 'Введите числовое значение'
                await edit_msg(keys=await profile_edit_kb())
                await asyncio.sleep(1.5)
                current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
                await edit_msg(keys=await profile_edit_kb())

        elif ch_city_mode == 1:
            var_city = msg.lower()
            try:
                mgr.weather_at_place(var_city)
                profile_city = var_city.title()
                ch_city_mode = 0
            except Exception as err:
                print('city existing\n', err)
                current_bot_txt_img[0] = 'Пожалуйста, введите существующий город'
                await edit_msg(keys=await profile_edit_kb())
                await asyncio.sleep(1.5)
                current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
                await edit_msg(keys=await profile_edit_kb())

        elif ch_desc_mode == 1:
            profile_description = msg
            ch_desc_mode = 0

        elif ch_photo_mode == 1:
            if msg == '' and dp.event.get('object').get('message').get('attachments')[0].get('type') == 'photo':
                photo_name = f'vk{dp.user_id}'
                current_bot_txt_img[0] = 'Загружаем изображение'
                await edit_msg(keys=profile_edit_kb)

                photo_url = dp.event.get('object').get('message').get('attachments')[0].get('photo').get(
                    'sizes')[-1].get('url')
                urllib.request.urlretrieve(photo_url, f"../user_profile_photos/{photo_name}.jpg")

                image = Image.open(f'../user_profile_photos/{photo_name}.jpg')
                resize_k = image.width / 300
                image = image.resize((round(image.width / resize_k), round(image.height / resize_k)))
                image.save(f'../user_profile_photos/{photo_name}.jpg')

                ch_photo_mode = 0
            else:
                current_bot_txt_img[0] = 'Пожалуйста, загрузие фото'
                await edit_msg(keys=await profile_edit_kb())
                await asyncio.sleep(1.5)
                current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
                await edit_msg(keys=await profile_edit_kb())

        else:
            registration_mode = 0
            await dp.send_message(text='Что-бы открыть меню - нажмите /start', keyboard=key_start)

        if 1 not in [ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode] and registration_mode == 1:
            current_bot_txt_img = [f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}',
                                   photo_name]
            await dp.send_message(text=current_bot_txt_img[0], attachment=await upload_photo(current_bot_txt_img[1]),
                                  keyboard=await profile_edit_kb())
            await bot.execute("messages.delete", peer_id=bot_main_msg_id[1], message_ids=bot_main_msg_id[0]-2, delete_for_all=1)
# ======================================================================================================================
# ==================================================================================================================CHAT
    elif CHAT_MODE == 1:
        t = time.localtime()
        datetime_current = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        cur.execute(
            'INSERT INTO `msgs` ('
            '`platform_1`, `platform_2`, `user1_id`, `user2_id`, `message`, `datetime`, `processed`) '
            'VALUES ('
            f'"vk", "{chat_user_platform}", {dp.user_id}, {chat_user_platform_id}, "{msg}", "{datetime_current}", 0)')
        conn.commit()
# ======================================================================================================================
    else:
        await dp.send_message(text='Что-бы открыть меню - нажмите /start', keyboard=key_start)


@bot.handle
@Handler.on("message_event")
async def handler(dp: Dispatcher):
    global bot_main_msg_id, chat_user_platform, chat_user_platform_id, CHAT_MODE, stop_thread
    global profile_name, photo_name, profile_age, profile_city, profile_description, profile_gender
    global ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode, registration_mode
    global current_bot_txt_img

    callback = dp.event.get('object').get('payload').get('type')
    user_id = dp.event.get('object').get('user_id')
# ===============================================================================================================Профиль
    if callback == 'create_profile':
        profile_name = '-----------'
        profile_age = '--'
        profile_city = '--------'
        profile_description = '--------------------------------<br>------------------<br>----------'
        photo_name = '0'
        profile_gender = '0'

        current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
        current_bot_txt_img[1] = photo_name
        await edit_msg(keys=await profile_edit_kb())
        registration_mode = 1
        ch_name_mode = ch_age_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0

    elif callback == 'edit_profile':
        conn.reset_session()
        cur.execute(f"SELECT * FROM `profiles` WHERE `platform`='vk' AND `platform_id`={user_id}")
        profile = cur.fetchone()
        profile_name, photo_name, profile_age, profile_gender, profile_description, profile_city = [profile[i] for i in
                                                                                                    (3, 4, 5, 6, 7, 8)]

        current_bot_txt_img[1] = photo_name
        current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
        await edit_msg(keys=await profile_edit_kb())
        registration_mode = 1
        ch_name_mode = ch_age_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0

    elif callback == 'cancel_profile_edit':
        registration_mode = 0
        current_bot_txt_img = ['Меню', 'media']
        await edit_msg(keys=await main_menu_create(user_id))

    elif callback in ['ch_name', 'ch_age', 'ch_city', 'ch_desc', 'ch_photo', 'profile_empty_callback']:
        global profile_kb

        if callback == 'profile_empty_callback':
            current_bot_txt_img[0] = 'Просто напишите данные в чат'
            await edit_msg(keys=await profile_edit_kb())
            current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
            await asyncio.sleep(1.5)
            await edit_msg(keys=await profile_edit_kb())

        else:
            if callback == 'ch_name':
                ch_age_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0
                ch_name_mode = 1
                profile_kb = await profile_edit_kb(name='Как вас зовут?', call_N='profile_empty_callback')

            elif callback == 'ch_age':
                ch_name_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0
                ch_age_mode = 1
                profile_kb = await profile_edit_kb(age='Сколько вам лет?', call_A='profile_empty_callback')

            elif callback == 'ch_city':
                ch_name_mode = ch_age_mode = ch_photo_mode = ch_desc_mode = 0
                ch_city_mode = 1
                profile_kb = await profile_edit_kb(city='Откуда вы?', call_C='profile_empty_callback')

            elif callback == 'ch_desc':
                ch_name_mode = ch_age_mode = ch_city_mode = ch_photo_mode = 0
                ch_desc_mode = 1
                profile_kb = await profile_edit_kb(desc='Расскажите о себе', call_D='profile_empty_callback')

            elif callback == 'ch_photo':
                ch_name_mode = ch_age_mode = ch_city_mode = ch_desc_mode = 0
                ch_photo_mode = 1
                profile_kb = await profile_edit_kb(photo='Загрузите фото', call_P='profile_empty_callback')

            current_bot_txt_img[0] = f'{profile_name}, {profile_age}<br>{profile_city}<br><br>{profile_description}'
            await edit_msg(keys=profile_kb)

    elif callback == 'ch_gender':
        ch_name_mode = ch_age_mode = ch_city_mode = ch_desc_mode = ch_photo_mode = 0
        await edit_msg(keys=gender_choice)

    elif callback in ['m', 'f']:
        await edit_msg(keys=await profile_edit_kb())
        profile_gender = callback

    elif callback == 'save_profile':
        global profile_existing
        print(1)

        if profile_existing == 1:
            cur.execute(
                f"UPDATE `profiles` SET `name` = '{profile_name}', `photo` = '{photo_name}', `age` = {profile_age}, "
                f"`gender` = '{profile_gender}', `description` = '{profile_description}', `city` = '{profile_city}' "
                f"WHERE `platform` = 'vk' AND `platform_id` = {user_id}")
            conn.commit()
            print(21)
        elif profile_existing == 0:
            cur.execute(
                f"INSERT INTO `profiles` (`platform`,`platform_id`,`name`,`photo`,`age`,`gender`,`description`,`city`) "
                f"VALUES ('vk', {user_id}, '{profile_name}', '{photo_name}', {profile_age}, '{profile_gender}', "
                f"'{profile_description}', '{profile_city}')"
            )
            conn.commit()
            print(22)

        registration_mode = 0
        current_bot_txt_img = ['Профиль сохранён', 'media']
        await edit_msg(keys=await main_menu_create(user_id))
        # await dp.send_message(text=current_bot_txt_img[0], attachment=await upload_photo(current_bot_txt_img[1]),
        #                       keyboard=await main_menu_create(user_id))
        print(3)

# ======================================================================================================================
# ==========================================================================================================Предпочтения
    elif callback == 'prefs':
        current_bot_txt_img = ['Кого вы хотите найти?', 'media']
        await edit_msg(keys=pref_gender_kb)

    elif callback in ['pref_m', 'pref_f', 'pref_gender_no_matter', 'pref_18-25', 'pref_25-35', 'pref_35+',
                      'pref_age_no_matter', 'pref_city_matter', 'pref_city_no_matter']:
        global pref_column_value, pref_column_name

        if callback in ['pref_m', 'pref_f', 'pref_gender_no_matter']:
            pref_gender_dict = {'pref_m': '"m"', 'pref_f': '"f"', 'pref_gender_no_matter': '`gender`'}
            pref_column_value = pref_gender_dict[callback]
            pref_column_name = '`pref_gender`'
            current_bot_txt_img[0] = 'Какого возраста?'
            await edit_msg(pref_age_kb)

        elif callback in ['pref_18-25', 'pref_25-35', 'pref_35+', 'pref_age_no_matter']:
            pref_age_dict = {'pref_18-25': 1, 'pref_25-35': 2, 'pref_35+': 3, 'pref_age_no_matter': 0}
            pref_column_value = pref_age_dict[callback]
            pref_column_name = '`pref_age`'
            current_bot_txt_img[0] = 'Откуда?'
            await edit_msg(pref_city_kb)

        elif callback in ['pref_city_matter', 'pref_city_no_matter']:
            pref_city_matter_dict = {'pref_city_matter': 1, 'pref_city_no_matter': 0}
            pref_column_value = pref_city_matter_dict[callback]
            pref_column_name = '`pref_city_matter`'
            current_bot_txt_img[0] = 'Ваши предпочтения сохранены'
            await edit_msg(await main_menu_create(user_id))

            cur.execute(f"UPDATE `profiles` SET `completed` = 1 "
                        f"WHERE `platform` = 'vk' AND `platform_id` = {user_id}")
            conn.commit()

        cur.execute(f"UPDATE `profiles` SET {pref_column_name} = '{pref_column_value}' "
                    f"WHERE `platform` = 'vk' AND `platform_id` = {user_id}")
        conn.commit()
        conn.reset_session()
# ======================================================================================================================
# ==================================================================================================================ROLL
    elif callback in ['roll_profiles', 'next_profile', 'previous_profile', 'select_profile', 'roll_chats',
                      'next_chat', 'previous_chat', 'select_chat', 'clear_chat']:
        global profile_offset, last_profile, pref_age, pref_gender, city_matter, city, user_fid, city_dict, age_dict
        global user_name, user_age, user_description, user_city, chat_member_id, background_check_db, user_photo

# ======================================================================================================Смотреть Профили
        if callback in ['roll_profiles', 'next_profile', 'previous_profile', 'select_profile']:

            if callback in ['roll_profiles', 'next_profile', 'previous_profile']:

                conn.reset_session()
                cur.execute(f"SELECT `pref_age`, `pref_gender`, `pref_city_matter`, `city`, `photo` FROM `profiles` "
                            f"WHERE `platform` = 'vk' AND `platform_id` = {user_id} LIMIT 1")

                age_dict = {'0': '= `age`', '1': '> 17 AND `age` < 25', '2': '> 24 AND `age` < 35', '3': '> 35'}
                [pref_age, pref_gender, city_matter, city, user_fid] = cur.fetchone()
                city_dict = {'0': '`city`', '1': f"'{city}'"}

                if callback == 'roll_profiles':
                    profile_offset = 0
                    try:
                        cur.execute(
                            f"SELECT COUNT(`photo`) FROM `profiles` WHERE `age` {age_dict[pref_age]} "
                            f"AND `gender` = {pref_gender} AND `city` = {city_dict[city_matter]} "
                            f"AND `photo` <> '{user_fid}' LIMIT 1 OFFSET {profile_offset}")
                        last_profile = int(cur.fetchone()[0]) - 1
                    except Exception as err: print('count last profile\n', err)

                elif callback in ['next_profile', 'previous_profile']:
                    if callback == 'next_profile':
                        profile_offset = profile_offset + 1 if profile_offset < last_profile else last_profile
                    else:
                        profile_offset = profile_offset - 1 if profile_offset > 0 else 0

                try:
                    cur.execute(
                        f"SELECT `platform`, `platform_id`, `name`, `photo`, `age`, `description`, `city` "
                        f"FROM `profiles` WHERE `age` {age_dict[pref_age]} AND `gender` = {pref_gender} "
                        f"AND `city` = {city_dict[city_matter]} AND `photo` <> '{user_fid}' "
                        f"LIMIT 1 OFFSET {profile_offset}")

                    [chat_user_platform, chat_user_platform_id, user_name, user_photo, user_age, user_description, user_city] = cur.fetchone()
                    chat_member_id = [chat_user_platform, chat_user_platform_id]

                    current_bot_txt_img = [f'{user_name}, {user_age}<br>{user_city}<br><br>{user_description}', user_photo]
                    await edit_msg(keys=profiles)

                except Exception as err:
                    print('roll profiles\n', err)
                    m = current_bot_txt_img[0]
                    current_bot_txt_img[0] = 'для вас ещё не нашлись подходящие кандидаты'
                    await edit_msg(keys=profiles)
                    current_bot_txt_img[0] = m
                    await asyncio.sleep(1.5)
                    await edit_msg(keys=profiles)

            elif callback == 'select_profile':
                CHAT_MODE = 1
                await edit_msg(keys=key_stop)
                await bot.execute("messages.send", peer_id=user_id,
                                  message='Вы вошли в режим переписки, что бы выйти нажмите stop', random_id=0)

                stop_thread = False
                background_check_db = Thread(await check_new_msgs_current_chat(user_id, chat_member_id))
                background_check_db.start()

# ======================================================================================================================
# ====================================================================================================Смотреть сообщения

        elif callback in ['roll_chats', 'next_chat', 'previous_chat', 'select_chat', 'clear_chat']:

            if callback in ['roll_chats', 'next_chat', 'previous_chat']:

                conn.reset_session()
                cur.execute(f'SELECT DISTINCT `platform_1`, `user1_id` FROM `msgs` '
                            f'WHERE `platform_2` = "vk" AND `user2_id` = {user_id};')

                chats_list = cur.fetchall()
                last_profile = len(chats_list) - 1

                if callback == 'roll_chats':
                    profile_offset = 0
                elif callback in ['next_chat', 'previous_chat']:
                    if callback == 'next_chat':
                        profile_offset = profile_offset + 1 if profile_offset < last_profile else last_profile
                    else:
                        profile_offset = profile_offset - 1 if profile_offset > 0 else 0

                try:
                    cur.execute(
                        f"SELECT `platform`, `platform_id`, `name`, `photo`, `age`, `description`, `city` "
                        f"FROM `profiles` WHERE `platform` = '{chats_list[profile_offset][0]}' "
                        f"AND `platform_id` = {chats_list[profile_offset][1]}")

                    [chat_user_platform, chat_user_platform_id, user_name, user_photo, user_age, user_description, user_city] = cur.fetchone()
                    chat_member_id = [chat_user_platform, chat_user_platform_id]

                    current_bot_txt_img = [f'{user_name}, {user_age}<br>{user_city}<br><br>{user_description}', user_photo]
                    await edit_msg(keys=chats)

                except Exception as err: print('roll chats\n', err)

            elif callback == 'select_chat':
                CHAT_MODE = 1
                await edit_msg(keys=key_stop)
                await dp.send_message(text='Вы вошли в режим переписки, что бы выйти нажмите stop')
                stop_thread = False
                background_check_db = Thread(await check_new_msgs_current_chat(user_id, chat_member_id))
                background_check_db.start()

            elif callback == 'clear_chat':
                try:
                    cur.execute(f"UPDATE `msgs` SET `processed` = 1 "
                                f"WHERE `platform_2` = 'vk' AND `user2_id` = {user_id} "
                                f"AND `platform_1` = '{chat_user_platform}' AND `user1_id` = {chat_user_platform_id}")
                    conn.commit()

                    current_bot_txt_img[0] = 'Новые сообщения этого пользователя удалены'
                    await edit_msg(keys=chats)
                except Exception as err: print('clear chat', err)


async def main_menu_create(user_id):
    global profile_existing
    conn.reset_session()

    inline_main_menu = {
        "buttons": [],
        "inline": True}
    try:
        cur.execute(
            f"SELECT `db_id` FROM `profiles` WHERE `platform` = 'vk' AND `platform_id` = {user_id} AND `completed` = 1")
        int(cur.fetchone()[0])
        profile_existing = 1

        inline_main_menu['buttons'].append([
            {"action": {
                "type": "callback", "payload": {'type': 'roll_profiles'},
                "label": "Смотреть анкеты"}, "color": "primary"}
        ])

        try:
            cur.execute(
                f"SELECT `db_id` FROM `msgs` WHERE (`platform_1` = 'vk' AND `user1_id` = {user_id}) "
                f"OR (`platform_2` = 'vk' AND `user2_id` = {user_id})")
            a = cur.fetchall()

            if a != []:
                try:
                    conn.reset_session()
                    cur.execute(f"SELECT COUNT(`db_id`) FROM `msgs` "
                                f"WHERE `platform_2` = 'vk' AND `user2_id` = {user_id} AND `processed` = 0")
                    new_msgs_count = int(cur.fetchone()[0])
                except Exception as err:
                    print('new msgs count\n', err)
                    new_msgs_count = 0

                new_msgs_count = f' ({new_msgs_count})' if new_msgs_count != 0 else ''
                inline_main_menu['buttons'].append([
                    {"action": {
                        "type": "callback", "payload": {'type': 'roll_chats'},
                        "label": f"Чаты{new_msgs_count}"}, "color": "primary"}
                ])

        except Exception as err:
            print('main menu chats existing\n', err)

        inline_main_menu['buttons'].append([
            {"action": {
                "type": "callback", "payload": {'type': 'edit_profile'},
                "label": "Изменить анкету"}, "color": "secondary"}
        ])
        inline_main_menu['buttons'].append([{"action": {
            "type": "callback", "payload": {'type': 'prefs'},
            "label": "Предпочтения"}, "color": "secondary"}
        ])

    except Exception as err:
        print('main menu profile completed\n', err)
        try:
            cur.execute(
                f"SELECT `db_id` FROM `profiles` WHERE `platform` = 'vk' AND `platform_id` = {user_id}")
            int(cur.fetchone()[0])
            inline_main_menu['buttons'].append([
                {"action": {
                    "type": "callback", "payload": {'type': 'edit_profile'},
                    "label": "Изменить анкету"}, "color": "secondary"}
            ])
            inline_main_menu['buttons'].append([{"action": {
                "type": "callback", "payload": {'type': 'prefs'},
                "label": "Предпочтения"}, "color": "secondary"}
            ])
            profile_existing = 1

        except Exception as err:
            print('main menu profile existing\n', err)

            inline_main_menu['buttons'].append([
                {"action": {
                    "type": "callback", "payload": {'type': 'create_profile'},
                    "label": "Зарегистрироваться"}, "color": "secondary"}
            ])
            profile_existing = 0

    inline_main_menu = json.dumps(inline_main_menu, ensure_ascii=False).encode("UTF-8")
    inline_main_menu = str(inline_main_menu.decode("UTF-8"))
    return inline_main_menu


async def check_new_msgs_current_chat(user_id, chat_member) -> None:
    global new_msg_current_chat, db_id, stop_thread
    cursor = conn.cursor()
    while True:
        conn.reset_session()
        await asyncio.sleep(0.5)
        try:
            sql = (f"SELECT `message`, `db_id` FROM `msgs` WHERE `platform_2` = 'vk' AND `user1_id` = {chat_member[1]} "
                   f"AND `platform_1` = '{chat_member[0]}' AND `user2_id` = {user_id} AND `processed` = 0 "
                   f"ORDER BY `msgs`.`datetime` ASC LIMIT 1")
            cursor.execute(sql)
            response = cursor.fetchall()[0]
            print(response)
            new_msg_current_chat = response[0]
            db_id = response[1]

            try:
                await bot.execute("messages.send", peer_id=user_id, message=new_msg_current_chat, random_id=0)
                cursor.execute(f'UPDATE `msgs` SET `processed` = 1 WHERE `db_id` = {db_id}')
                conn.commit()
            except Exception as err:
                print('>>check_new_msgs_current_chat processed\n', err)
        except IndexError:
            pass
        except Exception as err:
            print('>>check_new_msgs_current_chat\n', err)

        global stop_thread
        if stop_thread:
            break

while True:
    try:
        if __name__ == "__main__":
            run_polling(bot)
    except:
        pass
    asyncio.sleep(5)
