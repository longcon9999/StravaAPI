import datetime
import pandas as pd

from telegram import Bot, InputMediaDocument
from model import User
NAME_TOOL = "StravaAPI v1.0.0"


def date_to_timestamp(_date):
    try:
        return datetime.datetime.strptime(_date, "%d/%m/%Y").timestamp()
    except Exception as e:
        print(e)
        return None


def timestamp_to_date(_timestamp):
    try:
        return datetime.datetime.fromtimestamp(_timestamp).strftime("%d/%m/%Y")
    except Exception as e:
        print(e)
        return None


def get_data_csv(path):
    try:
        df = pd.read_csv(path, encoding="utf-8", na_filter=False)
        users = []
        print(df)
        for i in range(df.shape[0]):
            line = df.loc[i][:].to_list()
            user = User(_id=line[0],
                        _name=line[1],
                        _team=line[2],
                        _client_id=line[3],
                        _client_secret=line[4],
                        _code=line[5],
                        _access_token=line[6],
                        _refresh_token=line[7])
            users.append(user)
        return users, None
    except Exception as e:
        return None, f"{e}"


def update_data_csv(path, data):
    header = ['STT', 'Họ và tên', 'Đội', 'Client ID', 'Client Secret', 'Code', 'Access Token', 'Refresh Token',
              'URL Get Code']
    try:
        df = pd.DataFrame(data)
        df.to_csv(path, header=header, index=False, encoding="utf-8")
        return True, path
    except Exception as e:
        return False, f"{e}"


def send_tele(mess, user_id="-892018722", files=None, _type=""):
    api_key = "2083132609:AAEapKh1l5AMGC5DrzJe91YplrbQKvUQ5Eg"
    bot = Bot(token=api_key)
    _try = 10
    while _try > 0:
        _try -= 1
        try:
            if _type == "error":
                ic = "❌❌❌"
            elif _type == "done":
                ic = "✅✅✅"
            else:
                ic = "⚠️⚠️⚠️"
            if files:
                # if len(files) == 1:
                #     with open(files[0], "rb") as document:
                #         bot.send_document(chat_id=user_id,
                #                           filename=files[0],
                #                           document=document,
                #                           caption=f"From [{NAME_TOOL}]\n{ic}\n{mess}")
                # else:
                media_group = list()
                for i in range(len(files)):
                    file = files[i]
                    caption = None
                    if i == len(files) - 1:
                        caption = f"From [{NAME_TOOL}]\n{ic}️\n{mess}"
                    with open(file, "rb") as fin:
                        fin.seek(0)
                        media_group.append(InputMediaDocument(fin, caption=caption))
                bot.send_media_group(chat_id=user_id,
                                     media=media_group)
            else:
                bot.send_message(chat_id=user_id,
                                 text=f"From [{NAME_TOOL}]\n{ic}️\n{mess}")
            return
        except Exception as e:
            bot.send_message(chat_id=user_id,
                             text=f"From [{NAME_TOOL}]\n❌❌❌\n{mess}\n👉Send file error\n{e}\nTry {_try} times left")