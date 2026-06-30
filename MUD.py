import sys
import importlib.util

if importlib.util.find_spec("rich") is None:
    print("This program uses the 'rich' library for enhanced console output.")
    print("Please install it by typing the following command in the terminal:\n")
    print("    pip install rich\n")
    input("Press Enter to exit and try again after installation...")
    sys.exit(1)

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from base64 import b64encode, b64decode
import pyDes
import threading
import socket
import json
import random
import os
import time
import datetime

console = Console()
print_lock = threading.Lock()

p = 19
g = 2
active_users = []
chat_history = {}
last_contact_ip = None

def slow_print(text, delay=0.02, style=None):
    with print_lock:
        for char in text:
            console.print(char, end="", style=style)
            time.sleep(delay)
        console.print()

def ascii_banner():
    banner = """
   ███╗   ███╗██╗   ██╗██████╗ 
   ████╗ ████║██║   ██║██╔══██╗
   ██╔████╔██║██║   ██║██████╔╝
   ██║╚██╔╝██║██║   ██║██╔═══╝ 
   ██║ ╚═╝ ██║╚██████╔╝██║     
   ╚═╝     ╚═╝ ╚═════╝ ╚═╝     
-- Minimal User Protocol -- P2P --
    """
    slow_print(banner, 0.01, style="bold blue")

ascii_banner()
USERNAME_FILE = "username.txt"

if os.path.exists(USERNAME_FILE):
    with open(USERNAME_FILE, "r") as f:
        username = f.read().strip()
        slow_print(f"Welcome back, {username}!", 0.03, style="bold green")
else:
    slow_print("Enter your name:", 0.03, style="bold blue")
    username = Prompt.ask("")
    with open(USERNAME_FILE, "w") as f:
        f.write(username)
    slow_print(f"Welcome, {username}!", 0.03, style="bold green")

def print_message_bubble(sender, message, sent=True, secure=False):
    security_label = "(SECURE)" if secure else "(UNSECURE)"
    console.print()
    bubble = Panel(
        f"{message}",
        title=f"{sender} {'(SENT)' if sent else '(RECEIVED)'} {security_label}",
        border_style="green" if sent else "yellow",
        padding=(1, 2),
        expand=False,
        subtitle=" ",
        subtitle_align="left"
    )
    console.print(bubble)

def log_message(direction, ip, message, secure):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SECURE" if secure else "UNSECURE"
        user_display = ip
        for user in active_users:
            if user['ip'] == ip:
                user_display = user['username'] + f" ({ip})"
                break
        f.write(f"[{timestamp}] {direction.upper()} [{status}] {user_display}: {message}\n")

def udp_broadcast():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    local_ip = socket.gethostbyname(socket.gethostname())
    while True:
        message = json.dumps({"username": username, "ip": local_ip}).encode("utf-8")
        udp_socket.sendto(message, ("192.168.1.255", 6000))
        time.sleep(8)

def udp_listener():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("", 6000))
    while True:
        data, addr = udp_socket.recvfrom(1024)
        user_info = json.loads(data.decode("utf-8"))
        if user_info["username"] != username:
            exists = False
            for user in active_users:
                if user['username'] == user_info['username'] and user['ip'] == user_info['ip']:
                    user['last_seen'] = time.time()
                    exists = True
                    break
            if not exists:
                active_users.append({
                    "username": user_info["username"],
                    "ip": user_info["ip"],
                    "last_seen": time.time()
                })
                slow_print(f"{user_info['username']} just came online!", 0.01, style="bold cyan")

def tcp_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("", 6001))
    tcp_socket.listen()
    while True:
        conn, addr = tcp_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def handle_client(conn, addr):
    secure = False
    shared_secret = None
    data = conn.recv(1024).decode("utf-8")
    try:
        received_json = json.loads(data)
        if "key" in received_json:
            private_key = random.randint(1, p - 1)
            public_key = pow(g, private_key, p)
            peer_public_key = received_json["key"]
            shared_secret = pow(int(peer_public_key), private_key, p)

            response = json.dumps({"key": public_key})
            conn.send(response.encode("utf-8"))

            data = conn.recv(1024).decode("utf-8")
            received_json = json.loads(data)
            if "encrypted message" in received_json:
                encrypted_message = b64decode(received_json["encrypted message"])
                key = str(shared_secret).zfill(24)[:24].encode()
                cipher = pyDes.triple_des(key, padmode=pyDes.PAD_PKCS5)
                decrypted_message = cipher.decrypt(encrypted_message).decode()
                secure = True
                message = decrypted_message
            else:
                message = "[Encrypted message could not be received]"
        elif "encrypted message" in received_json:
            message = "[Encrypted but no key exchange]"
            secure = True
        elif "unencrypted message" in received_json:
            message = received_json["unencrypted message"]
        else:
            message = data
    except json.JSONDecodeError:
        message = data

    sender_info = addr[0]
    for user in active_users:
        if user['ip'] == addr[0]:
            sender_info = user['username'] + f" ({addr[0]})"
            break
    print_message_bubble(sender_info, message.strip(':'), sent=False, secure=secure)
    log_message("received", addr[0], message, secure)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history.setdefault(addr[0], []).append(("received", message, timestamp))
    conn.close()

def tcp_client(ip, message, secure=False):
    global last_contact_ip
    last_contact_ip = ip
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_socket.connect((ip, 6001))
    except socket.error:
        slow_print(f"Can not connect to {ip}.", 0.02, style="bold red")
        return

    if secure:
        private_key = random.randint(1, p - 1)
        public_key = pow(g, private_key, p)
        exchange_msg = json.dumps({"key": public_key})
        tcp_socket.send(exchange_msg.encode("utf-8"))

        data = tcp_socket.recv(1024).decode("utf-8")
        received_json = json.loads(data)
        peer_public_key = received_json.get("key")
        shared_secret = pow(int(peer_public_key), private_key, p)

        key = str(shared_secret).zfill(24)[:24].encode()
        cipher = pyDes.triple_des(key, padmode=pyDes.PAD_PKCS5)
        encrypted_message = cipher.encrypt(message.encode())
        final_msg = json.dumps({"encrypted message": b64encode(encrypted_message).decode()})
        tcp_socket.send(final_msg.encode("utf-8"))
    else:
        final_msg = json.dumps({"unencrypted message": message})
        tcp_socket.send(final_msg.encode("utf-8"))

    sender_name = ip
    for user in active_users:
        if user['ip'] == ip:
            sender_name = user['username'] + f" ({ip})"
            break
    print_message_bubble(sender_name, message, sent=True, secure=secure)
    log_message("sent", ip, message, secure)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history.setdefault(ip, []).append(("sent", message, timestamp))
    tcp_socket.close()


def show_active_users():
    if active_users:
        slow_print("\nActive Users:", 0.02, style="bold cyan")
        for user in active_users:
            status = "Online" if time.time() - user['last_seen'] <= 10 else "Away"
            slow_print(f"{user['username']} | {user['ip']} | {status}", 0.02, style="yellow")
    else:
        slow_print("No active users found.", 0.02, style="bold red")

def show_chat_history():
    if chat_history:
        slow_print("\nUsers you have chat history with:", 0.02, style="bold cyan")
        for user_ip in chat_history:
            name_display = user_ip
            for user in active_users:
                if user['ip'] == user_ip:
                    name_display = f"{user['username']} ({user_ip})"
                    break
            slow_print(f"- {name_display}", 0.02, style="yellow")
        slow_print("Enter the username or IP address to view chat history:", 0.02, style="bold green")
        selected = Prompt.ask("")
        found_ip = selected
        for user in active_users:
            if user['username'].lower() == selected.lower():
                found_ip = user['ip']
                break
        if found_ip in chat_history:
            slow_print(f"\nChat history with {found_ip}:", 0.02, style="bold magenta")
            for entry in chat_history[found_ip]:
                direction, msg, timestamp = entry
                security_info = "SECURE" if "key" in msg else "UNSECURE"
                console.print(f"[{timestamp}] {direction.upper()} [{security_info}]: {msg}", style="white")
        else:
            slow_print("You have no chat history with this user.", 0.02, style="bold red")
    else:
        slow_print("No chat history found.", 0.02, style="bold red")

threading.Thread(target=udp_broadcast, daemon=True).start()
threading.Thread(target=udp_listener, daemon=True).start()
threading.Thread(target=tcp_server, daemon=True).start()

while True:
    slow_print("Enter a command (type 'help' for available commands):", 0.02, style="bold cyan")
    command = Prompt.ask("").lower()

    if command == "q":
        break
    elif command == "users":
        show_active_users()
    elif command == "chat":
        if not active_users:
            slow_print("No active users available. Please wait for users to appear.", 0.02, style="bold red")
            continue
        show_active_users()
        slow_print("Enter the IP address or username of the user you want to message:", 0.02, style="bold green")
        target = Prompt.ask("")
        slow_print("Enter your message:", 0.02, style="bold green")
        message = Prompt.ask("")
        slow_print("Send as a secure message? (y/n):", 0.02, style="bold green")
        secure_choice = Prompt.ask("").lower() in ["y", "yes"]
        target_ip = None
        for user in active_users:
            if user['username'].lower() == target.lower():
                target_ip = user['ip']
                break
        if target_ip is None:
            try:
                socket.inet_aton(target)
                target_ip = target
            except socket.error:
                slow_print("Username or IP address not found.", 0.02, style="bold red")
                continue
        tcp_client(target_ip, message, secure=secure_choice)
    elif command == "sendlast":
        if last_contact_ip:
            slow_print("Enter your message:", 0.02, style="bold green")
            message = Prompt.ask("")
            slow_print("Send as a secure message? (y/n):", 0.02, style="bold green")
            secure_choice = Prompt.ask("").lower() in ["y", "yes"]
            tcp_client(last_contact_ip, message, secure=secure_choice)
        else:
            slow_print("No previous contact found.", 0.02, style="bold red")
    elif command == "history":
        show_chat_history()
    elif command == "help":
        slow_print("""\n--- Commands ---\n\n[Users] Show active users\n[Chat] Start a chat with a user\n[sendlast] Send a message to the last contacted user\n[History] Show chat history\n[help] Show this help message\n[q] Exit the program\n""", 0.02, style="cyan")

slow_print("Press Enter to exit...", 0.02, style="bold red")
input()

