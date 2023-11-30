import decimal
from random import uniform

from starknet_py.contract import Contract

from modules.base_classes.base_account import BaseAccount
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.utils import decimal_to_int
from modules.utils.logger import logger
from modules.utils.token_storage import nets_weth, eth
from modules.utils.token import WRAPPED_TOKEN_ABI, STARK_TOKEN_ABI

class Orbiter:
    STARK_ABI = [{"name":"Uint256","size":2,"type":"struct","members":[{"name":"low","type":"felt","offset":0},{"name":"high","type":"felt","offset":1}]},{"name":"transferERC20","type":"function","inputs":[{"name":"_token","type":"felt"},{"name":"_to","type":"felt"},{"name":"_amount","type":"Uint256"},{"name":"_ext","type":"felt"}],"outputs":[]}]

    ABI = [{"inputs":[{"internalType":"address payable","name":"_to","type":"address"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transfer","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transferERC20","outputs":[],"stateMutability":"nonpayable","type":"function"}]

    chaincodes = {
        'ethereum'      : '9001',
        'optimism'      : '9007',
        'bsc'           : '9015',
        'arbitrum'      : '9002',
        'nova'          : '9016',
        'polygon'       : '9006',
        'polygon_zkevm' : '9017',
        'zksync'        : '9014',
        'starknet'      : '9004',
        "zksync_lite"   : "9003",
        "linea"         : '9023'
    }

    orbiter_chaincodes_eth = {
        'ethereum'      : 0.000000000000009001,
        'optimism'      : 0.000000000000009007,
        'bsc'           : 0.000000000000009015,
        'arbitrum'      : 0.000000000000009002,
        'nova'          : 0.000000000000009016,
        'polygon'       : 0.000000000000009006,
        'polygon_zkevm' : 0.000000000000009017,
        'zksync'        : 0.000000000000009014,
        'starknet'      : 0.000000000000009004,
        "zksync_lite"   : 0.000000000000009003,
        "linea"         : 0.000000000000009023
    }

    buff_contracts = {
        "bsc"      : "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc",
        "arbitrum" : "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc",
        "polygon"  : "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc",
        "zksync"   : "0xBF3922a0cEBbcD718e715e83d9187cC4BbA23f11",
        "linea"    : "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc",
        "optimism" : "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc",
        "scroll"   : "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc",
    }

    contracts = {
        "bsc"      : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "zksync"   : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "optimism" : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "scroll"   : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "linea"    : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "arbitrum" : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "polygon"  : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "starknet" : 0x0173f81c529191726c6e7287e24626fe24760ac44dae2a1f7e02080230f8458b

    }

    def __init__(self, account: BaseAccount, recipient: str):
        self.account = account
        self.recipient = recipient

    def get_value_with_chaincode(self, value, net):
        base_num_dec = decimal.Decimal(str(value))
        orbiter_amount_dec = decimal.Decimal(str(self.orbiter_chaincodes_eth[net]))
        difference = base_num_dec - orbiter_amount_dec
        random_offset = decimal.Decimal(str(uniform(-0.000000000000001, 0.000000000000001)))
        result_dec = difference + random_offset
        orbiter_str = self.chaincodes[net][-4:]
        result_str = '{:.18f}'.format(result_dec.quantize(decimal.Decimal('0.000000000000000001')))
        result_str = result_str[:-4] + orbiter_str
        return decimal.Decimal(result_str)
    
    async def bridge_native_to_starknet(self, amount, net_name):
        try:
            w3 = self.account.get_w3(net_name)
            txn_data_handler = TxnDataHandler(self.account, net_name, w3=w3)

            amount = self.get_value_with_chaincode(amount, "starknet")
            value = decimal_to_int(amount, 18)
            if value <= 0:
                logger.error(f"[{self.account.evm_address}] orbiter value is 0")
                return -1
            contract = w3.eth.contract(self.buff_contracts[net_name], abi=self.ABI)
            txn = await contract.functions.transfer(
                self.contracts[net_name], 
                f"0x03{self.recipient[2::]}"
            ).build_transaction(await txn_data_handler.get_txn_data(value=value))


            return txn
        except Exception as e:
            logger.error(f"[{self.account.evm_address}] got error: {e}")
            return -1
        
    async def bridge_weth_to_stark(self, amount, net_name):
        w3 = self.account.get_w3(net_name)
        txn_data_handler = TxnDataHandler(self.account, net_name, w3=w3)

        amount = self.get_value_with_chaincode(amount, "starknet")
        value = decimal_to_int(amount, 18)
        
        if value <= 0:
            logger.error(f"[{self.account.evm_address}] orbiter value is 0")
            return -1
        weth = nets_weth[net_name]
        await weth.get_approve_txn(self.account, self.buff_contracts[net_name], value, w3=w3)
        contract = w3.eth.contract(self.buff_contracts[net_name], abi=self.ABI)
        
        txn = await contract.functions.transferERC20(
            weth.contract_address,
            self.contracts[net_name],
            value,
            "0x03" + self.recipient[2::]
        ).build_transaction(await txn_data_handler.get_txn_data())

        return txn
    
    async def bridge_from_stark(self, amount, net_name):
        
        amount = self.get_value_with_chaincode(amount, net_name)
        value = decimal_to_int(amount, 18)
        account = self.account.stark_native_account

        eth_contract = Contract(eth.contract_address, STARK_TOKEN_ABI, account)

        approve_call = eth_contract.functions["approve"].prepare(
            self.contracts["starknet"], value
        )
        contract = Contract(self.contracts["starknet"], self.STARK_ABI, account)
        call = contract.functions["transferERC20"].prepare(
            eth.contract_address,
            0x64a24243f2aabae8d2148fa878276e6e6e452e3941b417f3c33b1649ea83e11,
            int(value),
            int(self.recipient, 16)
        )

        calldata = [approve_call, call]

        return calldata