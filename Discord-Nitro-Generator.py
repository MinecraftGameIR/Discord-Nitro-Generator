import random
import string
import json
import requests
import threading
import time
import sys
import signal
import os

COLORS = {
    'reset': '\033[0m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'bold': '\033[1m'
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def current_time_hour():
    return time.strftime("%H:%M:%S")

def print_banner():
    clear()
    banner = f"""
{COLORS['cyan']}{COLORS['bold']}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ███╗   ██╗██╗████████╗██████╗  ██████╗                ║
║   ████╗  ██║██║╚══██╔══╝██╔══██╗██╔═══██╗               ║
║   ██╔██╗ ██║██║   ██║   ██████╔╝██║   ██║               ║
║   ██║╚██╗██║██║   ██║   ██╔══██╗██║   ██║               ║
║   ██║ ╚████║██║   ██║   ██║  ██║╚██████╔╝               ║
║   ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝                ║
║                                                          ║
║                   By Minecraft Game                      ║
╚══════════════════════════════════════════════════════════╝
{COLORS['reset']}
    """
    print(banner)

running = True
codes_generated = 0
valid_codes = 0
invalid_codes = 0
valid_codes_list = []

def signal_handler(sig, frame):
    global running
    print(f"\n{COLORS['yellow']}[!] Stopping...{COLORS['reset']}")
    running = False
    print(f"\n{COLORS['cyan']}══════════════════════════════════════════════════════════{COLORS['reset']}")
    print(f"{COLORS['bold']}{COLORS['white']}Statistics:{COLORS['reset']}")
    print(f"{COLORS['green']}✓ Valid:   {valid_codes}{COLORS['reset']}")
    print(f"{COLORS['red']}✗ Invalid: {invalid_codes}{COLORS['reset']}")
    print(f"{COLORS['blue']}📊 Total:  {codes_generated}{COLORS['reset']}")
    if valid_codes_list:
        print(f"\n{COLORS['bold']}{COLORS['white']}Valid Codes:{COLORS['reset']}")
        for code in valid_codes_list:
            print(f"{COLORS['green']}{code}{COLORS['reset']}")
    print(f"\n{COLORS['yellow']}[!] Bye!{COLORS['reset']}")
    time.sleep(2)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def send_webhook(webhook_url, nitro_code):
    try:
        payload = {
            'embeds': [{
                'title': '🎁 Valid Nitro Found!',
                'description': f'```{nitro_code}```',
                'color': 0x00FF00,
                'footer': {
                    'text': 'By Minecraft Game'
                },
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            }],
            'username': 'Nitro Gen',
            'avatar_url': 'https://cdn.discordapp.com/attachments/1041819334969937931/1234567890123456789/nitro.png'
        }
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code in [200, 204]
    except:
        return False

def generate_nitro_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=16))

def check_nitro_code(code):
    try:
        url = f'https://discord.com/api/v10/entitlements/gift-codes/{code}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        return response.status_code == 200
    except:
        return False

def worker(webhook_url=None):
    global codes_generated, valid_codes, invalid_codes, running, valid_codes_list
    while running:
        try:
            code = generate_nitro_code()
            full_url = f'https://discord.gift/{code}'
            codes_generated += 1
            if check_nitro_code(code):
                valid_codes += 1
                valid_codes_list.append(full_url)
                print(f"{COLORS['green']}[{current_time_hour()}] [VALID] {full_url}{COLORS['reset']}")
                if webhook_url:
                    send_webhook(webhook_url, full_url)
            else:
                invalid_codes += 1
                print(f"{COLORS['red']}[{current_time_hour()}] [INVALID] {full_url}{COLORS['reset']}")
            time.sleep(0.3)
        except:
            continue

def main():
    global running
    print_banner()
    print(f"{COLORS['cyan']}══════════════════════════════════════════════════════════{COLORS['reset']}")
    use_webhook = input(f"{COLORS['yellow']}[?] Use webhook? (y/n): {COLORS['reset']}").lower().strip()
    webhook_url = None
    if use_webhook in ['y', 'yes']:
        webhook_url = input(f"{COLORS['yellow']}[?] Webhook URL: {COLORS['reset']}").strip()
        try:
            test = {'content': 'test'}
            requests.post(webhook_url, json=test, timeout=5)
            print(f"{COLORS['green']}[✓] Webhook OK{COLORS['reset']}")
        except:
            print(f"{COLORS['red']}[✗] Bad webhook{COLORS['reset']}")
            webhook_url = None
    try:
        num_threads = int(input(f"{COLORS['yellow']}[?] Threads (1-20): {COLORS['reset']}"))
        num_threads = max(1, min(20, num_threads))
    except:
        num_threads = 5
    try:
        max_codes = input(f"{COLORS['yellow']}[?] Max codes (Enter for no limit): {COLORS['reset']}")
        if max_codes.strip():
            max_codes = int(max_codes)
        else:
            max_codes = None
    except:
        max_codes = None
    print(f"{COLORS['cyan']}══════════════════════════════════════════════════════════{COLORS['reset']}")
    print(f"{COLORS['green']}[✓] Starting {num_threads} threads...{COLORS['reset']}")
    print(f"{COLORS['yellow']}[!] Press Ctrl+C to stop{COLORS['reset']}")
    print(f"{COLORS['cyan']}══════════════════════════════════════════════════════════{COLORS['reset']}")
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(webhook_url,), daemon=True)
        t.start()
        threads.append(t)
    try:
        if max_codes:
            target = codes_generated + max_codes
            while running and codes_generated < target:
                time.sleep(0.1)
            running = False
            for t in threads:
                t.join(timeout=1)
            signal_handler(None, None)
        else:
            while running:
                time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{COLORS['red']}[✗] Error: {str(e)}{COLORS['reset']}")
        input()