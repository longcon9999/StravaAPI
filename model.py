import json
import logging


class User:

    def __init__(self, _id, _name, _team, _client_id, _client_secret, _code, _access_token, _refresh_token):
        self.id = _id
        self.name = _name
        self.team = _team
        self.client_id = _client_id
        self.client_secret = _client_secret
        self.code = _code
        self.access_token = _access_token
        self.refresh_token = _refresh_token
        self.url_get_code = f"https://www.strava.com/oauth/authorize?client_id={_client_id}&redirect_uri=https" \
                            f"://localhost/exchangetoken&response_type=code&scope=activity:read_all" \
            if _client_id is not None and _client_secret != "" else None

    def to_json(self):
        return {
            "id": str(self.id) if self.id is not None else None,
            "name": self.name,
            "team": str(self.team) if self.team is not None else None,
            "client_id": str(self.client_id) if self.client_id is not None else None,
            "client_secret": self.client_secret,
            "code": self.code,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "url_get_code": self.url_get_code
        }

    def to_list(self):
        return [
            self.id, self.name, self.team, self.client_id, self.client_secret, self.code, self.access_token,
            self.refresh_token, self.url_get_code
        ]

    def __repr__(self):
        return json.dumps(self.to_json(), indent=4, sort_keys=False, ensure_ascii=False)


class Activity:

    def __init__(self, _json_data):
        self.json_data = _json_data
        self.name = _json_data.get("name")
        self.distance = _json_data.get("distance")
        self.moving_time = _json_data.get("moving_time")
        self.type = _json_data.get("type")
        self.sport_type = _json_data.get("sport_type")
        self.workout_type = _json_data.get("workout_type")
        self.id = _json_data.get("id")
        self.start_date = _json_data.get("start_date")
        self.start_date_local = _json_data.get("start_date_local")
        self.average_speed = _json_data.get("average_speed")
        self.max_speed = _json_data.get("max_speed")

    def to_list(self):
        # ["Tên", "Khoảng cách", "Thời gian", "Ngày thực hiện", "Tốc độ trung bình", "Tốc độ lớn nhất"]
        return [
            self.name, self.distance, self.moving_time, self.start_date_local, self.average_speed, self.max_speed
        ]

    def __repr__(self):
        return json.dumps(self.json_data, indent=4, sort_keys=False, ensure_ascii=False)


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
