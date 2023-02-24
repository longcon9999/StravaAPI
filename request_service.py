import requests

from model import Activity


class StravaAPI:

    def __init__(self, _client_id, _client_secret, _client_code, _access_token, _refresh_token):
        self.client_id = _client_id
        self.client_secret = _client_secret
        self.client_code = _client_code
        self.access_token = _access_token
        self.refresh_token = _refresh_token

    def post_get_token(self):

        url = "https://www.strava.com/oauth/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": self.client_code,
            "grant_underscore": "authorization_code"
        }

        response = requests.post(url, params=params)
        if response.ok:
            response_json = response.json()
            access_token = response_json.get("access_token")
            refresh_token = response_json.get("refresh_token")
            if access_token is not None and access_token != "":
                self.access_token = access_token
            if refresh_token is not None and refresh_token != "":
                self.refresh_token = refresh_token

        return self.access_token, self.refresh_token

    def post_refresh_token(self):
        url = "https://www.strava.com/oauth/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, params=params)
        if response.ok:
            response_json = response.json()
            access_token = response_json.get("access_token")
            refresh_token = response_json.get("refresh_token")
            if access_token is not None and access_token != "":
                self.access_token = access_token
            if refresh_token is not None and refresh_token != "":
                self.refresh_token = refresh_token

        return self.access_token, self.refresh_token

    def get_activities(self, before=None, after=None):
        activities = []
        page = 1
        try:
            while True:
                url = "https://www.strava.com/api/v3/athlete/activities"
                params = {
                    "after": after,
                    "before": before,
                    "page": page,
                    "per_page": 100
                }
                headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }

                response = requests.get(url, headers=headers, params=params)
                if response.ok:
                    response_json = response.json()
                    if len(response_json) == 0:
                        return activities, None
                    for item in response_json:
                        activity = Activity(_json_data=item)
                        activities.append(activity)
                    page += 1
                else:
                    response_json = response.json()
                    return None, response_json
        except Exception as e:
            return None, f"{e}"
