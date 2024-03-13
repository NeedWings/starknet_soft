from random import randint, shuffle

from starknet_py.contract import Contract
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId 
from starknet_py.net.account.account import Account as StarkNativeAccount
from starknet_py.net.models.transaction import Invoke
from loguru import logger as console_log

from modules.other.bids import bidder
from modules.other.dmail import dmail_hand
from modules.other.starkstars import starkstars
from modules.other.upgrader import upgrader
from modules.other.key_changer import key_changer
from modules.other.starkrocket import StarkRocket
from modules.config import SETTINGS, NEW_PRIVATE_KEYS, NEW_PAIRS
from modules.base_classes.base_account import BaseAccount
from modules.utils.logger import logger
from modules.utils.utils import get_random_value_int, sleeping, handle_dangerous_request, normalize_to_32_bytes
from modules.utils.token_storage import eth
from modules.utils.braavos_deploy_utils import deploy_account_braavos

ARGENT = 1
BRAAVOS = 2


class OtherHandler:

    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    async def dmail(self):
        amount = get_random_value_int(SETTINGS["dmail_messages_amount"])
        for _ in range(amount):
            
            calldata = await dmail_hand.create_txn_for_dmail(self.account)

            await self.account.send_txn_starknet(calldata)

            await sleeping(self.account.stark_address)

    async def bids(self, type_):
        for _ in range(get_random_value_int(SETTINGS["bids_amount"])):
            if type_ == 1:
                await self.account.send_txn_starknet(await bidder.create_txn_for_flex(eth, self.account))
            elif type_ == 2:
                await self.account.send_txn_starknet(await bidder.create_txn_for_unframed(eth, self.account))
            elif type_ == 3:
                await self.account.send_txn_starknet(await bidder.create_txn_for_element(eth, self.account))
            await sleeping(self.account.stark_address)

    async def starkstars(self):
        if SETTINGS["do not mint minted"]:
            contracts = starkstars.contracts.copy()
            new_contracts = []
            logger.info(f"[{self.account.stark_address}] checking minted nfts")
            amount = get_random_value_int(SETTINGS["starkstars_nft_amount"])
            for address in contracts:
                contract = Contract(address, starkstars.ABI, self.account.stark_native_account, cairo_version=1)
                have = (await handle_dangerous_request(
                    contract.functions["balance_of"].call,
                    "can't get NFT info",
                    self.account.stark_address,
                    self.account.stark_native_account.address
                ))[0]
                if not have:
                    new_contracts.append(address)
            shuffle(new_contracts)
            if len(new_contracts) < amount:
                amount = len(new_contracts)
            for i in range(amount):
                logger.info(f"[{self.account.stark_address}] going to mint starkstars nft")
                calldata = await starkstars.create_tnx_for_mint(self.account, eth, contract_address=new_contracts[i])
                await self.account.send_txn_starknet(calldata)
                await sleeping(self.account.stark_address)
        else:

            for _ in range(get_random_value_int(SETTINGS["starkstars_nft_amount"])):
                logger.info(f"[{self.account.stark_address}] going to mint starkstars nft")
                #calldata = await starkstars.asd(self.account)
                calldata = await starkstars.create_tnx_for_mint(self.account, eth)
                await self.account.send_txn_starknet(calldata)
                await sleeping(self.account.stark_address)

    async def starknet_id(self):
        for _ in range(get_random_value_int(SETTINGS["starknet_id_amount"])):
            id_contract = Contract(0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af, [{"name":"mint","type":"function","inputs":[{"name":"starknet_id","type":"felt"}],"outputs":[]}], self.account.stark_native_account)
            logger.info(f"[{self.account.stark_address}] going to mint starknet id")
            call = id_contract.functions["mint"].prepare_call(
                randint(0, 999999999999)
            )
            calldata = [call]

            await self.account.send_txn_starknet(calldata)
            await sleeping(self.account.stark_address)

    async def upgrade(self, type_):
        if type_ == ARGENT:
            txn = await upgrader.upgrade_argent(self.account)
        elif type_ == BRAAVOS:
            txn = await upgrader.upgrade_braavos(self.account)

        logger.info(f"[{self.account.stark_address}] going to upgrade")
        await self.account.send_txn_starknet(txn)

    async def deployer(self):
        if SETTINGS["Provider"].lower() in ["argent_newest", "argent"]:
            class_hash = 0x01a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003

            key_pair = KeyPair.from_private_key(int(self.account.private_key, 16))
            salt = key_pair.public_key


            account_initialize_call_data = [key_pair.public_key, 0]

            call_data = [
                *account_initialize_call_data
            ]
        elif SETTINGS["Provider"].lower() == "braavos":
            class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
            key_pair = KeyPair.from_private_key(int(self.account.private_key, 16))
            salt = key_pair.public_key
            account_initialize_call_data = [key_pair.public_key]

            call_data = [
                0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
                0x2dd76e7ad84dbed81c314ffe5e7a7cacfb8f4836f01af4e913f275f89a3de1a,
                len(account_initialize_call_data),
                *account_initialize_call_data
            ]  
        else:
            console_log.error(f"Selecterd unsupported provider: {SETTINGS['Provider']}. Please use Argent or Braavos")
            input()
            exit() 
            return
        
        address = int(self.account.stark_address, 16)
        account = self.account.stark_native_account

        balance = 0
        while True:
            try:
                nonce = await account.get_nonce()
                if nonce > 0:
                    logger.info(f"[{self.account.stark_address}] already deployed. Skip")
                    return
                else:
                    break
            except Exception as e:
                if "contract not found" in (str(e)).lower():
                    nonce = 0
                    break
                logger.error(f"[{self.account.stark_address}] got error while trying to get nonce: {e}")
                await sleeping(self.account.stark_address, True)
        while True:
            
            logger.info(f"[{self.account.stark_address}] checking balance.")
            balance = (await self.account.get_balance_starknet(eth))[0]
            logger.info(f"[{self.account.stark_address}] got balance: {balance/1e18} ETH")
            if balance >= 1e14:
                break
            await sleeping(self.account.stark_address)
        logger.success(f"[{self.account.stark_address}] found balance. Going to deploy")
        i = 0
        while i < 10:
            i += 1
            try:
                provider = SETTINGS["Provider"].lower()
                if provider == "argent_newest" or provider == "argent":
                    account_deployment_result = await StarkNativeAccount.deploy_account(
                        address=account.address,
                        class_hash=class_hash,
                        salt=salt,
                        key_pair=account.signer.key_pair,
                        client=account.client,
                        chain=StarknetChainId.MAINNET,
                        constructor_calldata=call_data,
                        auto_estimate=True,
                    )
                elif provider == "braavos_newest":
                    account_deployment_result = await deploy_account_braavos(
                        address=account.address,
                        class_hash=class_hash,
                        salt=salt,
                        key_pair=account.signer.key_pair,
                        client=account.client,
                        chain=StarknetChainId.MAINNET,
                        constructor_calldata=call_data,
                        auto_estimate=True,
                        )
                else:
                    logger.error(f"Selected unsupported wallet provider: {SETTINGS['Provider'].lower()}. Please select one of this: argen_newest, braavos_newest")
                    return

                # Wait for deployment transaction to be accepted

                await account_deployment_result.wait_for_acceptance()
                # From now on, account can be used as usual
                account = account_deployment_result.account
                logger.success(f"[{self.account.stark_address}] deployed successfully, txn hash: {hex(account_deployment_result.hash)}")
                return 1

            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got error, while deploying account, {e}")
                await sleeping(self.account.stark_address, True)
        logger.error(f"[{self.account.stark_address}] got error")
        return -1
    
    async def change_owner(self):
        if self.account.stark_native_account.address not in list(NEW_PAIRS.keys()):
            logger.error(f"[{self.account.stark_address}] can't find new key")
            return
        new_public_key = normalize_to_32_bytes(hex(NEW_PAIRS[self.account.stark_native_account.address]))
        if new_public_key not in list(NEW_PRIVATE_KEYS.keys()):
            logger.error(f"[{self.account.stark_address}] can't find private key in new_private_keys.txt file")
            return
        new_private_key = NEW_PRIVATE_KEYS[new_public_key]

        txn = await key_changer.create_txn_for_changing_key(int(new_private_key, 16), self.account)
        logger.info(f"[{self.account.stark_address}] going to change owner to key with public key {new_public_key}")
        await self.account.send_txn_starknet(txn)

    async def mint_rocket(self):
        logger.info(f"[{self.account.stark_address}] going to mint stark rocket")
        stark_rocket = StarkRocket(self.account)
        txn = await stark_rocket.get_txn()

        await self.account.send_txn_starknet(txn)
        