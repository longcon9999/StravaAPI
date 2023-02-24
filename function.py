import datetime
import pandas as pd

from model import User
NAME_TOOL = ""


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
