import json

key_start = {
    "one_time": True,
    "buttons": [
        [
            {"action": {
                "type": "text",
                "label": "start"},
                "color": "primary"}
        ]]}
key_start = json.dumps(key_start, ensure_ascii=False).encode("UTF-8")
key_start = str(key_start.decode("UTF-8"))

key_stop = {
    "buttons": [
        [
            {"action": {
                "type": "text",
                "label": "stop"},
                "color": "secondary"}
        ]]}
key_stop = json.dumps(key_stop, ensure_ascii=False).encode("UTF-8")
key_stop = str(key_stop.decode("UTF-8"))


async def profile_edit_kb(name='Имя', age='Возраст', city='Город', desc='Описание', photo='Фото', call_N="ch_name", call_A='ch_age', call_C='ch_city', call_D='ch_desc', call_P='ch_photo'):
    profile_kb = {
        "buttons": [
            [
                {"action": {
                    "type": "callback",
                    "payload": {"type": f"{call_N}"},
                    "label": f"{name}"},
                    "color": "secondary"},
                {"action": {
                    "type": "callback",
                    "payload": {"type": f"{call_A}"},
                    "label": f"{age}"},
                    "color": "secondary"}
            ],
            [
                {"action": {
                    "type": "callback",
                    "payload": {"type": f"{call_C}"},
                    "label": f"{city}"},
                    "color": "secondary"},
                {"action": {
                    "type": "callback",
                    "payload": {"type": f"{call_D}"},
                    "label": f"{desc}"},
                    "color": "secondary"}
            ],
            [
                {"action": {
                    "type": "callback",
                    "payload": {"type": "ch_gender"},
                    "label": "Пол"},
                    "color": "secondary"},
                {"action": {
                    "type": "callback",

                    "payload": {"type": f"{call_P}"},
                    "label": f"{photo}"},
                    "color": "secondary"}
            ],
            [
                {"action": {
                    "type": "callback",
                    "payload": {"type": "save_profile"},
                    "label": "Сохранить"},
                    "color": "secondary"},
                {"action": {
                    "type": "callback",
                    "payload": {"type": "cancel_profile_edit"},
                    "label": "Отмена"},
                    "color": "secondary"}
            ]
        ], "inline": True}
    profile_kb = json.dumps(profile_kb, ensure_ascii=False).encode("UTF-8")
    profile_kb = str(profile_kb.decode("UTF-8"))
    return profile_kb

gender_choice = {
    "buttons": [
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "m"},
                "label": "Мужской"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "f"},
                "label": "Женский"},
                "color": "secondary"}
        ]], "inline": True}
gender_choice = json.dumps(gender_choice, ensure_ascii=False).encode("UTF-8")
gender_choice = str(gender_choice.decode("UTF-8"))

pref_gender_kb = {
    "buttons": [
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_m"},
                "label": "Мужчину"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_f"},
                "label": "Женщину"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_gender_no_matter"},
                "label": "Не важно"},
                "color": "secondary"}
        ]], "inline": True}
pref_gender_kb = json.dumps(pref_gender_kb, ensure_ascii=False).encode("UTF-8")
pref_gender_kb = str(pref_gender_kb.decode("UTF-8"))

pref_age_kb = {
    "buttons": [
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_18-25"},
                "label": "18-25"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_25-35"},
                "label": "25-35"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_35+"},
                "label": "35+"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_age_no_matter"},
                "label": "Не важно"},
                "color": "secondary"}
        ]], "inline": True}
pref_age_kb = json.dumps(pref_age_kb, ensure_ascii=False).encode("UTF-8")
pref_age_kb = str(pref_age_kb.decode("UTF-8"))

pref_city_kb = {
    "buttons": [
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_city_matter"},
                "label": "В моём городе"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "pref_city_no_matter"},
                "label": "Не важно"},
                "color": "secondary"}
        ]], "inline": True}
pref_city_kb = json.dumps(pref_city_kb, ensure_ascii=False).encode("UTF-8")
pref_city_kb = str(pref_city_kb.decode("UTF-8"))

profiles = {
    "buttons": [
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "previous_profile"},
                "label": "<-"},
                "color": "secondary"},
            {"action": {
                "type": "callback",
                "payload": {"type": "next_profile"},
                "label": "->"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "select_profile"},
                "label": "Выбрать"},
                "color": "secondary"}
        ]], "inline": True}
profiles = json.dumps(profiles, ensure_ascii=False).encode("UTF-8")
profiles = str(profiles.decode("UTF-8"))

chats = {
    "buttons": [
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "previous_chat"},
                "label": "<-"},
                "color": "secondary"},
            {"action": {
                "type": "callback",
                "payload": {"type": "clear_chat"},
                "label": "🚫"},
                "color": "secondary"},
            {"action": {
                "type": "callback",
                "payload": {"type": "next_chat"},
                "label": "->"},
                "color": "secondary"}
        ],
        [
            {"action": {
                "type": "callback",
                "payload": {"type": "select_chat"},
                "label": "Выбрать"},
                "color": "secondary"}
        ]], "inline": True}
chats = json.dumps(chats, ensure_ascii=False).encode("UTF-8")
chats = str(chats.decode("UTF-8"))
