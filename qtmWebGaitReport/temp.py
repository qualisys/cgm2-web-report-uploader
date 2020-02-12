import requests
import json


def get_upload_token(input_url, client_id):
    url_base = input_url + "/api/v2/"
    url = url_base + "auth/upload/token"
    headers = {"Content-Type": "application/json"}
    r = requests.post(
        url=url, json={"clientId": client_id}, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
        raise Exception
    uploadToken = json.loads(r.text)["jwt"]
    return uploadToken
