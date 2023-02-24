import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

from function import timestamp_to_date
from request_service import StravaAPI


class ThreadCrawl(QThread):

    sender_status = pyqtSignal(int, str)
    logs = pyqtSignal(int, str)
    token = pyqtSignal(int, str, str)

    def __init__(self, _users, _time_before=None, _time_after=None):
        QThread.__init__(self)
        self.users = _users
        self.time_before = _time_before
        self.time_after = _time_after

    def run(self) -> None:
        try:
            self.logs.emit(0, f"Bắt đầu: before {timestamp_to_date(_timestamp=self.time_before)} - "
                              f"after {timestamp_to_date(_timestamp=self.time_after)}")
            lines = []
            for i in range(len(self.users)):
                user = self.users[i]
                self.logs.emit(0, f"Lấy dữ liệu của {user.name} đội {user.team} client id {user.client_id}")
                strava_api = StravaAPI(_client_id=user.client_id,
                                       _client_code=user.code,
                                       _client_secret=user.client_secret,
                                       _access_token=user.access_token,
                                       _refresh_token=user.refresh_token)
                activities, error = strava_api.get_activities(after=self.time_after, before=self.time_before)
                if activities is None:
                    access_token, refresh_token = strava_api.post_refresh_token()
                    activities, error = strava_api.get_activities(after=self.time_after, before=self.time_before)
                    if activities is None:
                        self.logs.emit(1, f"Lấy dữ liệu của {user.name} đội {user.team} client id {user.client_id} "
                                          f"lỗi {error}")
                        self.sender_status.emit(i, f"{error}")
                        continue
                    self.logs.emit(0, f"Cập nhật token của {user.name} đội {user.team} client id {user.client_id}")
                    self.logs.emit(0, f"Access token: {access_token}")
                    self.logs.emit(0, f"Refresh token: {refresh_token}")
                    self.token.emit(i, access_token, refresh_token)

                self.logs.emit(0, f"Đã lấy được {len(activities)} hoạt động")
                self.sender_status.emit(i, f"{len(activities)} hoạt động")
                # print(len(activities))
                for activity in activities:
                    if activity.type and activity.type.lower() == "run" and float(activity.max_speed) > 0:
                        line = [user.name, user.team, user.client_id]
                        line.extend(activity.to_list())
                        print(line)
                        lines.append(line)

            if len(lines) > 0:
                df = pd.DataFrame(lines)
                header = ["Họ và tên", "Đội", "Client ID", "Tên hoạt động", "Khoảng cách",
                          "Thời gian", "Ngày thực hiện", "Tốc độ trung bình", "Tốc độ lớn nhất"]
                df.to_csv("Output.csv", index=False, header=header, encoding="utf-8")

            self.logs.emit(2, "Hoàn thành")
        except Exception as e:
            self.logs.emit(1, f"Lỗi {e}")
        finally:
            self.logs.emit(3, "")


class ThreadGetToken(QThread):

    sender_status = pyqtSignal(int, str)
    logs = pyqtSignal(int, str)
    token = pyqtSignal(int, str, str)

    def __init__(self, _user, _index):
        QThread.__init__(self)
        self.user = _user
        self.index = _index

    def run(self) -> None:
        try:
            self.logs.emit(0, f"Lấy Token của {self.user.name} đội {self.user.team} client id {self.user.client_id}")
            strava_api = StravaAPI(_client_id=self.user.client_id,
                                   _client_code=self.user.code,
                                   _client_secret=self.user.client_secret,
                                   _access_token=self.user.access_token,
                                   _refresh_token=self.user.refresh_token)
            access_token, refresh_token = strava_api.post_get_token()
            self.logs.emit(0, f"Cập nhật token của {self.user.name} đội {self.user.team} client id "
                              f"{self.user.client_id}")
            self.logs.emit(0, f"Access token: {access_token}")
            self.logs.emit(0, f"Refresh token: {refresh_token}")
            self.token.emit(self.index, access_token, refresh_token)

            self.logs.emit(0, f"Đã lấy được token")
            self.sender_status.emit(self.index, f"Đã lấy được token")
            self.logs.emit(2, "Hoàn thành")
        except Exception as e:
            self.logs.emit(1, f"Lỗi {e}")
        finally:
            self.logs.emit(3, "")
