import datetime

import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

from function import timestamp_to_date, send_tele
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
            count = 0
            for i in range(len(self.users)):
                user = self.users[i]
                self.logs.emit(0, f"Lấy dữ liệu của {user.name} đội {user.team} client id {user.client_id}")
                if user.access_token is None or user.access_token == "" \
                        or user.refresh_token is None or user.refresh_token == "":
                    continue

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
                count += 1
                for activity in activities:
                    if float(activity.max_speed) > 0:
                        line = [user.name, user.team, user.client_id]
                        line.extend(activity.to_list())
                        print(line)
                        lines.append(line)

            if len(lines) > 0:
                df = pd.DataFrame(lines)
                header = ["Họ và tên", "Đội", "Client ID", "Tên hoạt động", "Thời gian", "Thời gian GTM", "Timezone",
                          "Khoảng cách (m)", "Thời gian thực hiện (s)", "Tốc độ trung bình (m/s)",
                          "Tốc độ lớn nhất (m/s)", "Loại"]
                now = datetime.datetime.now()
                current_time = now.strftime("%m_%d_%Y_%H_%M_%S")
                df.to_excel(f"Output_{current_time}.xlsx", index=False, header=header, sheet_name="Data")
                df.to_csv(f"Output_{current_time}.csv", index=False, header=header, encoding="utf-8")
                send_tele(mess=f"Hoàn thành lấy dữ liệu."
                               f"\nSố người tham gia: {len(self.users)}"
                               f"\nSố người lấy được thông tin: {count}"
                               f"\nThời gian trước: {timestamp_to_date(_timestamp=self.time_before)}"
                               f"\nThời gian sau: {timestamp_to_date(_timestamp=self.time_after)}",
                          files=[f"Output_{current_time}.xlsx", f"Output_{current_time}.csv"], _type="done",
                          user_id="987256640")

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
