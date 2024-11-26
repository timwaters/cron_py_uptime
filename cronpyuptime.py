#!/usr/bin/python3
print("Hello World!")
import requests
import yaml

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

headers = {'user-agent': 'tims-cron-py-uptime-bot/1'}

def check_head(site):
    url = site["url"]
    try:
        resp = requests.head(url, timeout=10, headers=headers)
        if (resp.status_code != 200):
            send_message(site, resp.status_code, "")
    except requests.exceptions.RequestException as e:
        send_message(site, 500,  f"RequestException: {e}")


def check_text(site):
    url = site["url"]
    string = site["string"]
    resp = requests.get(url, timeout=10, headers=headers)
    if (resp.status_code != 200):
        send_message(site, resp.status_code, "")
    elif (string not in resp.text):
        send_message(site, resp.status_code, string + " Text not found")

def send_message(site, status, msg):
    telegram_token = config["telegram_token"]
    telegram_chat = config["telegram_chat"]
    message = "messaage", site, status, msg
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_user}&text={message}"
    try:
        requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Error sending telegran chat ", f"RequestException: {e}")


# go over the sites
sites = config["sites"]

for site in sites:
    if site["monitor"] == "head":
        check_head(site)
    elif site["monitor"] == "text":
        check_text(site)

#finished. 