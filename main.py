import os
import multiprocessing
import main_old

def runner(stark_keys, eth_keys, task_number, proxy):
	os.environ['http_proxy'] = proxy
	os.environ['HTTP_PROXY'] = proxy
	os.environ['https_proxy'] = proxy
	os.environ['HTTPS_PROXY'] = proxy
	os.environ['no_proxy'] = '127.0.0.1, localhost'
	os.environ['NO_PROXY'] = '127.0.0.1, localhost'
	main_old.runner(stark_keys, eth_keys, task_number)

if __name__ == "__main__":
	task_number = int(input('Enter task number\n'))
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
