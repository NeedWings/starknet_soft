from cfg import *
import subprocess
import uuid, re
import hashlib
import socket

KEY = "CEy426oSSaOTWDPgtuKxm1nS2uWN_4-L_eyt0dmAr40="


def decrypt(filename):
    f = Fernet(KEY)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data.split(':')


server_data = decrypt(f"{SETTINGS_PATH}server_data.txt")
connect_data = (server_data[0], int(server_data[1]))

def check_license_elig(sha):
    logger.info("Checking license expiration date...")
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(connect_data)
        message = {
            "auth": 'starknet',
            "key": sha
        }
        client.send(json.dumps(message).encode())
        response = client.recv(1024).decode()
        client.close()
        if response == "True":
            return True
        else:
            logger.error(f'Cant auth your device/subs')
            input("Press any key to exit")
            exit()
    except Exception as error:
        logger.error(f'SEnd this message to dev: {error}')
        input("Press any key to exit")
        exit()

def hash_string(input_string: str) -> str:
    # Создание объекта sha256
    sha256 = hashlib.sha256()

    # Передача байтовой строки в функцию хеширования
    sha256.update(input_string.encode('utf-8'))

    # Получение и возврат хеша в шестнадцатеричном формате
    return sha256.hexdigest()


def get_serial_number():
    try:
        # Запуск shell-команды для получения серийного номера
        serial_number = subprocess.check_output("system_profiler SPHardwareDataType | awk '/Serial/ {print $4}'", shell=True).strip().decode("utf-8")
        return serial_number
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_disk_uuid():
    try:
        # Запуск shell-команды для получения UUID диска
        disk_uuid = subprocess.check_output("diskutil info / | awk '/Volume UUID/ {print $3}'", shell=True).strip().decode("utf-8")
        return disk_uuid
    except Exception as e:
        print(f"An error occurred while getting disk UUID: {e}")
        return None

def get_cpu_info():
    try:
        # Запуск shell-команды для получения информации о CPU
        cpu_info = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).strip().decode("utf-8")
        return cpu_info
    except Exception as e:
        print(f"An error occurred while getting CPU information: {e}")
        return None

def get_user_key():
    values = [
        get_cpu_info(), get_disk_uuid(), get_serial_number()
    ]
    if None in values:
        input("Cant generate api key, pls contact with support")
        return
    
    user_key = "mac_" + hash_string(''.join(i for i in values))
    return user_key

def checking_license():
    return check_license_elig(get_user_key())