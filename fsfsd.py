import requests


penis = 0

while penis < 1 or penis > 15:
    penis = int(input("Vvedite penis(1-15) "))
    r = requests.get(f"https://api.telegram.org/bot6342347907:AAGikS4TTJPHLlY6rCaJuC9zQmGy_c_J93U/sendMessage?text={penis}&chat_id=667970295")
    if penis > 15:
        print("ТЫ МЕНЬШЕ ПИЗДИ")


print(f'vash penis is {penis}')