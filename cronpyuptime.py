#!/usr/bin/python3
import requests
import yaml
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys

def send_message(config: dict, site: dict, status: int, msg: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        f"🚨 Alert at {timestamp}\n"
        f"Site: {site['name']}\n"
        f"URL: {site['url']}\n"
        f"Status: {status}\n"
        f"Message: {msg}"
    )
    
    url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
    params = {
        "chat_id": config['telegram_chat'],
        "text": message
    }
    
    try:
        with requests.Session() as session:
            response = session.post(url, params=params, timeout=10)
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")

def check_head(session: requests.Session, site: dict, config: dict) -> None:
    try:
        resp = session.head(site['url'], timeout=10)
        if resp.status_code != 200:
            send_message(config, site, resp.status_code, "Unexpected status code")
    except requests.exceptions.RequestException as e:
        send_message(config, site, 500, f"Request failed: {str(e)}")

def check_text(session: requests.Session, site: dict, config: dict) -> None:
    try:
        resp = session.get(site['url'], timeout=10)
        if resp.status_code != 200:
            send_message(config, site, resp.status_code, "Unexpected status code")
        elif 'string' in site and site['string'] and site['string'] not in resp.text:
            send_message(config, site, resp.status_code, f"Text '{site['string']}' not found")
    except requests.exceptions.RequestException as e:
        send_message(config, site, 500, f"Request failed: {str(e)}")

def main():
    # Load config
    try:
        with open("config.yml", 'r') as stream:
            config = yaml.safe_load(stream)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Create session with retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({'user-agent': 'tims-cron-py-uptime-bot/1.1'})

    # Check sites
    for site in config['sites']:
        if site['monitor'] == "head":
            check_head(session, site, config)
        elif site['monitor'] == "text":
            check_text(session, site, config)
        else:
            print(f"Unknown monitor type '{site['monitor']}' for site {site['name']}")

if __name__ == "__main__":
    main()
