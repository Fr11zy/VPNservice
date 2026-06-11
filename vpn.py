import os
import sys
import struct
import fcntl
import socket
import threading
import argparse

from database.db import Database
from models.users import Users
from werkzeug.security import check_password_hash

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000 

def create_tun(name, ip_addr):
    tun = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", name.encode(), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    
    os.system(f"ip addr add {ip_addr}/24 dev {name}")
    os.system(f"ip link set dev {name} up")
    return tun

def xor_encrypt(data, key=0x5A):
    return bytes(b ^ key for b in data)

def tun2udp(tun_fd, udp_sock, remote_addr):
    while True:
        try:
            packet = os.read(tun_fd, 2048)
            if not packet: break
            enc = xor_encrypt(packet)
            udp_sock.sendto(enc, remote_addr)
        except Exception as e:
            print(f"Error reading TUN: {e}")
            break

def udp2tun(tun_fd, udp_sock):
    while True:
        try:
            data, addr = udp_sock.recvfrom(4096)
            dec = xor_encrypt(data)
            os.write(tun_fd, dec)
        except Exception as e:
            print(f"Error reading UDP: {e}")
            break

def run_server():
    PORT = 1194
    db = Database("db.sqlite")
    
    print("Создаем интерфейс tun0 (IP: 10.0.0.1)")
    tun = create_tun("tun0", "10.0.0.1")
    
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("0.0.0.0", PORT))
    
    print(f"Ожидаем подключения на порту {PORT}...")
    
    while True:
        data, client_addr = udp.recvfrom(1024)
        credentials = data.decode('utf-8', errors='ignore').split(':')
        
        if len(credentials) == 2:
            username, password = credentials
            print(f"Попытка входа от пользователя: {username}")
            
            user = Users.find_by_username(db, username)
            if user and check_password_hash(user.Password, password):
                print("Авторизация успешна! Туннель открыт.")
                udp.sendto(b"AUTH_OK", client_addr)
                
                t1 = threading.Thread(target=tun2udp, args=(tun, udp, client_addr), daemon=True)
                t2 = threading.Thread(target=udp2tun, args=(tun, udp), daemon=True)
                t1.start()
                t2.start()
                t1.join()
            else:
                print("Неверный логин или пароль.")
                udp.sendto(b"AUTH_FAIL", client_addr)

def run_client(server_ip, username, password):
    PORT = 1194
    print("Создаем интерфейс tun1 (IP: 10.0.0.2)")
    tun = create_tun("tun1", "10.0.0.2")
    
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Отправка учетных данных на {server_ip}...")
    auth_data = f"{username}:{password}".encode()
    udp.sendto(auth_data, (server_ip, PORT))
    
    response, _ = udp.recvfrom(1024)
    if response == b"AUTH_OK":
        print("Успешно подключено к серверу!")
        t1 = threading.Thread(target=tun2udp, args=(tun, udp, (server_ip, PORT)), daemon=True)
        t2 = threading.Thread(target=udp2tun, args=(tun, udp), daemon=True)
        t1.start()
        t2.start()
        t1.join()
    else:
        print("[CLIENT] Ошибка: Неверный логин или пароль.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VPN Service")
    parser.add_argument("mode", choices=["server", "client"], help="Режим работы")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP сервера (для клиента)")
    parser.add_argument("--user", type=str, help="Username (для клиента)")
    parser.add_argument("--password", type=str, help="Password (для клиента)")
    
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server()
    elif args.mode == "client":
        if not args.user or not args.password:
            print("Для запуска клиента укажите --user и --password")
            sys.exit(1)
        run_client(args.ip, args.user, args.password)