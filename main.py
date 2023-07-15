import os
import multiprocessing
import main_old

from peewee import *

if __name__ == "__main__":
	i = 0
	options = []
	print('Choose your database\n')
	for file in os.listdir('data'):
		if file.endswith(".db"):
			print(f'{i} {file}')
			options.append(file)
			i += 1
	option = int(input('Enter number\n'))
	db = SqliteDatabase(f'data/{option}')

class Wallet(Model):
	walletId =   AutoField()
	#seedEncrypted = TextField()
	seed = TextField()
	walletAddress = TextField()
	walletKey = TextField()
	ethAddress = TextField()
	ethKey = TextField()
	class Meta:
		database = db

db.connect()

message = """
Enter task number

1 - Бридж ETH из Arb, Opti, Eth (Layerswap, Orbiter). Для начала, скрипт проверяет все сети на наличие валюты для бриджа. Если находит значение выше: MinEthValue (настройки), то делает бридж в старкнет

2 - Рандомные свапы на выбранных дексах (поддерживаются : anvu, myswap, jediswap, 10kswap, sithswap). Количество определяется настройкой SwapAmounts, стейблы выбираются из настройки Supported_tokens(USDT и USDC). Количество для свапа задается настройкой WorkPercent.

3 - Свап всех стейблов в ETH на случайном выбранном дексе

4 - Добавить ликвидность в случайный декс из выбранных (LiqDEXs) в количестве, которое задает параметр LiqWorkPercent

5 - Вывод всей ликвидности из всех выбранных дексов

6 - Starkgate, поддерживается только ETH. Настройки такие же, как и в первом модуле

7 - FULL модуль, включены все предыдущие модули, кроме бриджей

8 - Вывод денег из StarkNet в Arbitrum через Orbiter.

9 - На случай, если у вас остались стейблы после софта на л0, сбриджит их в арбитрум, свапнет на эфир и сделает бридж через орбитер

10 - Выводит в консоль поочередно адреса старкнета и ММ

11 - Шифрование ключей

12 - Генератор кошельков. Количество задается параметром AmountToCreate, файл, куда будут сохранятся ключи — OutFile

13 - Деплоер кошельков, будет ждать, пока на кошельке не появится ETH

14 - Квест от MySwap. Будет свапать ETH на wstETH и обратно, пока не будет 0.03 объем, дальше заминтит NFT\n
"""

def runner(stark_keys, eth_keys, task_number, proxy):
	os.environ['http_proxy'] = proxy
	os.environ['HTTP_PROXY'] = proxy
	os.environ['https_proxy'] = proxy
	os.environ['HTTPS_PROXY'] = proxy
	os.environ['no_proxy'] = '127.0.0.1, localhost'
	os.environ['NO_PROXY'] = '127.0.0.1, localhost'
	main_old.runner(stark_keys, eth_keys, task_number)

if __name__ == "__main__":
	task_number = int(input(message))
	poolnum = int(input('Enter load\n'))
	chunk_size = int(input('Enter chunk size\n'))
	with open('data/starknet_keys.txt', 'r') as f:
		stark_keys = f.read().splitlines()
	with open('data/eth_keys.txt') as f:
		eth_keys = f.read().splitlines()
	with open('data/proxyServers.txt') as f:
		proxyServers = f.read().splitlines()
	proxynum = len(proxyServers)
	args = []
	i = 0
	while stark_keys:
		args.append((stark_keys[:chunk_size], eth_keys[:chunk_size], task_number, proxyServers[i % proxynum]))
		stark_keys = stark_keys[chunk_size:]
		eth_keys = eth_keys[chunk_size:]
		i += 1
	print(f'Loaded {i} chunks')
	with multiprocessing.Pool(processes=poolnum) as s:
		s.starmap(runner, args)
	input("Finished\n")
