
import sys
import os
from platform import system
import socket
import hashlib
import getpass
import json
import asyncio

from loguru import logger as console_log
from cryptography.fernet import Fernet

from modules.utils.account import Account
from modules.config import SETTINGS_PATH, KEY, SETTINGS

PLATFORM = system()
if PLATFORM == "Windows":
    import wmi

    def decrypt(filename):
        f = Fernet(KEY)
        with open(filename, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data).decode()
        return decrypted_data.split(':')

    server_data = decrypt(f"{SETTINGS_PATH}server_data.txt")
    connect_data = (server_data[0], int(server_data[1]))

    def check_license_elig(sha):
        console_log.info("Checking license expiration date...")
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
                console_log.error(f'Cant auth your device/subs')
                input("Press any key to exit")
                exit()
        except Exception as error:
            console_log.error(f'SEnd this message to dev: {error}')
            input("Press any key to exit")
            exit()

    def checking_license():
        text = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID + ':SOFT'
        sha = hashlib.sha1(text.encode()).hexdigest()
        return check_license_elig(sha)

    if __name__ == "__main__":
        pass
        checking_license()

    def get_disks():
        c = wmi.WMI()
        logical_disks = {}
        for drive in c.Win32_DiskDrive():
            for partition in drive.associators("Win32_DiskDriveToDiskPartition"):
                for disk in partition.associators("Win32_LogicalDiskToPartition"):
                    logical_disks[disk.Caption] = {"model":drive.Model, "serial":drive.SerialNumber}
        return logical_disks

    def decode_secrets():
        console_log.info("Decrypting your secret keys..")
        logical_disks = get_disks()
        decrypt_type = SETTINGS["DecryptType"].lower()
        disk = SETTINGS["LoaderDisk"]
        if decrypt_type == "flash":
            disk_data = logical_disks[disk]
            data_to_be_encoded = disk_data["model"] + '_' + disk_data["serial"]
        elif decrypt_type == "password":
            data_to_be_encoded = getpass.getpass('[DECRYPTOR] Write here password to decrypt secret keys: ')
        key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="
        f = Fernet(key)
        while True:
            try:
                path = SETTINGS_PATH + 'encoded_secrets.txt'
                with open(path, 'rb') as file:
                    file_data = file.read()
                    break
            except Exception as error:
                console_log.error(f'Error with trying to open file encoded_secrets.txt! {error}')
                input("Fix it and press enter: ")
        try:
            return json.loads(f.decrypt(file_data).decode())
        except :
            console_log.error("Key to Decrypt files is incorrect!")
            return decode_secrets()

    def transform_keys(private_keys, addresses):
        counter = 0
        accounts = []
        for key in private_keys:
            key = private_keys[key]
            account = Account(key)
            stark_address = account.get_starknet_address_from_private(key)
            if account.evm_address.lower() in addresses or stark_address in addresses:
                counter +=1
                accounts.append(key) 
        return accounts, counter

    def encode_secrets():
        logical_disks = get_disks()
        while True:
            try:
                with open(SETTINGS_PATH + 'to_encrypted_secrets.txt', encoding='utf-8') as file:
                    data = file.readlines()
                    console_log.info(f'Found {len(data)} lines of keys')
                    break
            except Exception as error:
                console_log.error(f"Failed to open {SETTINGS_PATH + 'to_encrypted_secrets.txt'} | {error}")
                input("Create file and try again. Press any key to try again: ")

        json_wallets = {}
        for k in data:
            try:
                address = Account(k.replace("\n", "")).evm_address
                json_wallets.update({
                address.lower(): k.replace("\n", "")
                })
            except Exception as error:
                console_log.error(f'Cant add line: {k}')
        
        with open(SETTINGS_PATH + "data.txt", 'w') as file:
            json.dump(json_wallets, file)
        
        if SETTINGS["DecryptType"].lower() == 'flash':
            while True:
                answer = input(
                    "Write here disk name, like: 'D'\n" + \
                    ''.join(f"Disk name: {i.replace(':', '')} - {logical_disks[i]}\n" for i in logical_disks.keys())
                )
                agree = input(
                    f"OK, your disk with name: {answer} | Data: {logical_disks[answer + ':']}\n" + \
                    "Are you agree to encode data.txt using this data? [Y/N]: "
                )
                if agree.upper().replace(" ", "") == "Y":
                    break

            data = logical_disks[answer + ":"]
            data_to_encoded = data["model"] + '_' + data["serial"]
            key = hashlib.sha256(data_to_encoded.encode()).hexdigest()[:43] + "="

        elif SETTINGS["DecryptType"].lower() == 'password':
            while True:
                data_to_be_encoded = getpass.getpass('Write here password to encrypt secret keys: ')
                agree = input(
                    f"OK, Are you sure that password is correct?: {data_to_be_encoded[:4]}***\n" + \
                    "Are you agree to encode data.txt using this data? [Y/N]: "
                )  
                if agree.upper().replace(" ", "") == "Y":
                    break

            key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="

        f = Fernet(key)
        with open(SETTINGS_PATH + "data.txt", 'rb') as file:
            data_file = file.read()

        encrypted = f.encrypt(data_file)

        with open(SETTINGS_PATH + "encoded_secrets.txt", 'wb') as file:
            file.write(encrypted)
        
        os.remove(SETTINGS_PATH + "data.txt")
        open(SETTINGS_PATH + "to_encrypted_secrets.txt", 'w')
        console_log.success(f'All is ok! Check to_run_addresses.txt and run soft again')
        input("Press any key to exit")
        sys.exit()
else:
    import subprocess
    def decrypt(filename):
        f = Fernet(KEY)
        with open(filename, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data).decode()
        return decrypted_data.split(':')


    server_data = decrypt(f"{SETTINGS_PATH}server_data.txt")
    connect_data = (server_data[0], int(server_data[1]))

    def check_license_elig(sha):
        console_log.info("Checking license expiration date...")
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
                console_log.error(f'Cant auth your device/subs')
                input("Press any key to exit")
                exit()
        except Exception as error:
            console_log.error(f'SEnd this message to dev: {error}')
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

    if __name__ == "__main__":
        pass
        checking_license()



    def decode_secrets():
        console_log.info("Decrypting your secret keys..")
        decrypt_type = SETTINGS["DecryptType"].lower()
        disk = SETTINGS["LoaderDisk"]
        if decrypt_type == "password":
            data_to_be_encoded = getpass.getpass('[DECRYPTOR] Write here password to decrypt secret keys: ')
        key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="
        f = Fernet(key)
        while True:
            try:
                path = SETTINGS_PATH + 'encoded_secrets.txt'
                with open(path, 'rb') as file:
                    file_data = file.read()
                    break
            except Exception as error:
                console_log.error(f'Error with trying to open file encoded_secrets.txt! {error}')
                input("Fix it and press enter: ")
        try:
            return json.loads(f.decrypt(file_data).decode())
        except :
            console_log.error("Key to Decrypt files is incorrect!")
            return decode_secrets()

    def transform_keys(private_keys, addresses):
        counter = 0
        accounts = []
        for key in private_keys:
            key = private_keys[key]
            account = Account(key)
            stark_address = account.get_starknet_address_from_private(key)
            if account.evm_address.lower() in addresses or stark_address in addresses:
                counter +=1
                accounts.append(key) 
        return accounts, counter

    def encode_secrets():
        while True:
            try:
                with open(SETTINGS_PATH + 'to_encrypted_secrets.txt', encoding='utf-8') as file:
                    data = file.readlines()
                    console_log.info(f'Found {len(data)} lines of keys')
                    break
            except Exception as error:
                console_log.error(f"Failed to open {SETTINGS_PATH + 'to_encrypted_secrets.txt'} | {error}")
                input("Create file and try again. Press any key to try again: ")

        json_wallets = {}
        for k in data:
            try:
                address = Account(k.replace("\n", "")).evm_address
                json_wallets.update({
                address.lower(): k.replace("\n", "")
                })
            except Exception as error:
                console_log.error(f'Cant add line: {k}')
        
        with open(SETTINGS_PATH + "data.txt", 'w') as file:
            json.dump(json_wallets, file)


        if SETTINGS["DecryptType"].lower() == 'password':
            while True:
                data_to_be_encoded = getpass.getpass('Write here password to encrypt secret keys: ')
                agree = input(
                    f"OK, Are you sure that password is correct?: {data_to_be_encoded[:4]}***\n" + \
                    "Are you agree to encode data.txt using this data? [Y/N]: "
                )  
                if agree.upper().replace(" ", "") == "Y":
                    break

            key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="

        f = Fernet(key)
        with open(SETTINGS_PATH + "data.txt", 'rb') as file:
            data_file = file.read()

        encrypted = f.encrypt(data_file)

        with open(SETTINGS_PATH + "encoded_secrets.txt", 'wb') as file:
            file.write(encrypted)
        
        os.remove(SETTINGS_PATH + "data.txt")
        open(SETTINGS_PATH + "to_encrypted_secrets.txt", 'w')
        console_log.success(f'All is ok! Check to_run_addresses.txt and run soft again')
        input("Press any key to exit")
        sys.exit()