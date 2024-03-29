from random import choice

from starknet_py.contract import Contract

from modules.base_classes.base_account import BaseAccount
from modules.utils.token import StarkToken
from modules.utils.utils import handle_dangerous_request


class StarkStars:

    contracts = [
        0x04d70758d392e0563a8a0076d4b72847048dea7d65199c50eabc8e855ca62931,
    0x02ac5be4b280f6625a56b944bab9d985fbbc9f180ff4b08b854b63d284b7f6ae,
    0x5f650c37f8a15e33f01b3c28365637ca72a536014c4b8f84271c20a4c24aef8,
    0x27c8cb6bf861df8b86ebda8656430aeec9c1c2c66e9f99d3c8587df5fcb1c9c,
    0x5e69ae81aed84dfadb4af03a67ce702e353db7f7f87ad833cf08df36e427704,
    0x6b1e710f97e0d4701123c256a6f4cce4ffdc2bf6f439b42f48d08585feab123,
    0x62b37f6ced8e742ecd4baa51321e0c39ab089183a1ca0b24138e1fb0f5083a8,
    0x656c27654b2b3c4ae3e8f5f6bc2a4863a79fb74cb7b2999af9dde2ad1fe3cb5,
    0x265f815955a1595e6859f3ad80533f15b2b57311d25fed6f01e4c530c1f1b0f,
    0x2c69468dd31a6837bc4a10357bc940f41f6d0acebe74376c940195915cede1d,
    0x40cb48ec6f61e1bbc5b62ee2f7a7df8151712394248c90db4f12f7a61ce993,
    0x4aa60106c215809a9dfc2ac2d64aa166f1185e9dc7212497a837f7d60bfb1c3,
    0x2ff063073208cd8b867c727be3a5f46c54d31ae1c1fbf7506ffaca673990f,
    0x7bc362ffdbd67ff80b49e95f0b9996ad89f9f6ea9186d209ece577df429e69b,
    0x267217f031a1d794446943ba45175153d18202b3db246db6b15b0c772f9ec09,
    0x21461d8b7593ef6d39a83229750d61a23b7f45b91baafb5ad1b2da6abf13c0,
    0x4c7999fb6eeb958240abdecdddc2331f35b5f99f1e60e29ef0e4e26f23e182b,
    0x50e02814bd1900efd33148dbed847e7fe42a2a2de6dd444366ead20cf8dedc5,
    0x3883b7148c475f170c4b1a21e37b15b9261e86f9c203098ff1c3b7f8cf72f73,
    0x394034029c6c0773397a2c79eb9b7df8f080613bfec83d93c3cd5e7c0b993ce,
    ]
    ABI = [{"name":"SRC5Impl","type":"impl","interface_name":"openzeppelin::introspection::interface::ISRC5"},{"name":"core::bool","type":"enum","variants":[{"name":"False","type":"()"},{"name":"True","type":"()"}]},{"name":"openzeppelin::introspection::interface::ISRC5","type":"interface","items":[{"name":"supports_interface","type":"function","inputs":[{"name":"interface_id","type":"core::felt252"}],"outputs":[{"type":"core::bool"}],"state_mutability":"view"}]},{"name":"SRC5CamelImpl","type":"impl","interface_name":"openzeppelin::introspection::interface::ISRC5Camel"},{"name":"openzeppelin::introspection::interface::ISRC5Camel","type":"interface","items":[{"name":"supportsInterface","type":"function","inputs":[{"name":"interfaceId","type":"core::felt252"}],"outputs":[{"type":"core::bool"}],"state_mutability":"view"}]},{"name":"ERC721MetadataImpl","type":"impl","interface_name":"openzeppelin::token::erc721::interface::IERC721Metadata"},{"name":"core::integer::u256","type":"struct","members":[{"name":"low","type":"core::integer::u128"},{"name":"high","type":"core::integer::u128"}]},{"name":"openzeppelin::token::erc721::interface::IERC721Metadata","type":"interface","items":[{"name":"name","type":"function","inputs":[],"outputs":[{"type":"core::felt252"}],"state_mutability":"view"},{"name":"symbol","type":"function","inputs":[],"outputs":[{"type":"core::felt252"}],"state_mutability":"view"},{"name":"token_uri","type":"function","inputs":[{"name":"token_id","type":"core::integer::u256"}],"outputs":[{"type":"core::felt252"}],"state_mutability":"view"}]},{"name":"ERC721MetadataCamelOnlyImpl","type":"impl","interface_name":"openzeppelin::token::erc721::interface::IERC721MetadataCamelOnly"},{"name":"openzeppelin::token::erc721::interface::IERC721MetadataCamelOnly","type":"interface","items":[{"name":"tokenURI","type":"function","inputs":[{"name":"tokenId","type":"core::integer::u256"}],"outputs":[{"type":"core::felt252"}],"state_mutability":"view"}]},{"name":"ERC721Impl","type":"impl","interface_name":"openzeppelin::token::erc721::interface::IERC721"},{"name":"core::array::Span::<core::felt252>","type":"struct","members":[{"name":"snapshot","type":"@core::array::Array::<core::felt252>"}]},{"name":"openzeppelin::token::erc721::interface::IERC721","type":"interface","items":[{"name":"balance_of","type":"function","inputs":[{"name":"account","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::integer::u256"}],"state_mutability":"view"},{"name":"owner_of","type":"function","inputs":[{"name":"token_id","type":"core::integer::u256"}],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"transfer_from","type":"function","inputs":[{"name":"from","type":"core::starknet::contract_address::ContractAddress"},{"name":"to","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_id","type":"core::integer::u256"}],"outputs":[],"state_mutability":"external"},{"name":"safe_transfer_from","type":"function","inputs":[{"name":"from","type":"core::starknet::contract_address::ContractAddress"},{"name":"to","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_id","type":"core::integer::u256"},{"name":"data","type":"core::array::Span::<core::felt252>"}],"outputs":[],"state_mutability":"external"},{"name":"approve","type":"function","inputs":[{"name":"to","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_id","type":"core::integer::u256"}],"outputs":[],"state_mutability":"external"},{"name":"set_approval_for_all","type":"function","inputs":[{"name":"operator","type":"core::starknet::contract_address::ContractAddress"},{"name":"approved","type":"core::bool"}],"outputs":[],"state_mutability":"external"},{"name":"get_approved","type":"function","inputs":[{"name":"token_id","type":"core::integer::u256"}],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"is_approved_for_all","type":"function","inputs":[{"name":"owner","type":"core::starknet::contract_address::ContractAddress"},{"name":"operator","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"view"}]},{"name":"ERC721CamelOnlyImpl","type":"impl","interface_name":"openzeppelin::token::erc721::interface::IERC721CamelOnly"},{"name":"openzeppelin::token::erc721::interface::IERC721CamelOnly","type":"interface","items":[{"name":"balanceOf","type":"function","inputs":[{"name":"account","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::integer::u256"}],"state_mutability":"view"},{"name":"ownerOf","type":"function","inputs":[{"name":"tokenId","type":"core::integer::u256"}],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"transferFrom","type":"function","inputs":[{"name":"from","type":"core::starknet::contract_address::ContractAddress"},{"name":"to","type":"core::starknet::contract_address::ContractAddress"},{"name":"tokenId","type":"core::integer::u256"}],"outputs":[],"state_mutability":"external"},{"name":"safeTransferFrom","type":"function","inputs":[{"name":"from","type":"core::starknet::contract_address::ContractAddress"},{"name":"to","type":"core::starknet::contract_address::ContractAddress"},{"name":"tokenId","type":"core::integer::u256"},{"name":"data","type":"core::array::Span::<core::felt252>"}],"outputs":[],"state_mutability":"external"},{"name":"setApprovalForAll","type":"function","inputs":[{"name":"operator","type":"core::starknet::contract_address::ContractAddress"},{"name":"approved","type":"core::bool"}],"outputs":[],"state_mutability":"external"},{"name":"getApproved","type":"function","inputs":[{"name":"tokenId","type":"core::integer::u256"}],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"isApprovedForAll","type":"function","inputs":[{"name":"owner","type":"core::starknet::contract_address::ContractAddress"},{"name":"operator","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"view"}]},{"name":"IStarkStarsImpl","type":"impl","interface_name":"achievments::contract::contract::IStarkStars"},{"name":"achievments::contract::contract::IStarkStars","type":"interface","items":[{"name":"get_price","type":"function","inputs":[],"outputs":[{"type":"core::integer::u256"}],"state_mutability":"view"},{"name":"mint","type":"function","inputs":[],"outputs":[],"state_mutability":"external"},{"name":"withdraw","type":"function","inputs":[],"outputs":[],"state_mutability":"external"},{"name":"set_price","type":"function","inputs":[{"name":"price","type":"core::integer::u256"}],"outputs":[],"state_mutability":"external"}]},{"name":"constructor","type":"constructor","inputs":[{"name":"recipient","type":"core::starknet::contract_address::ContractAddress"},{"name":"base_uri","type":"core::felt252"}]},{"kind":"struct","name":"achievments::contract::contract::Transfer","type":"event","members":[{"kind":"key","name":"from","type":"core::starknet::contract_address::ContractAddress"},{"kind":"key","name":"to","type":"core::starknet::contract_address::ContractAddress"},{"kind":"key","name":"token_id","type":"core::integer::u256"}]},{"kind":"struct","name":"achievments::contract::contract::Approval","type":"event","members":[{"kind":"key","name":"owner","type":"core::starknet::contract_address::ContractAddress"},{"kind":"key","name":"approved","type":"core::starknet::contract_address::ContractAddress"},{"kind":"key","name":"token_id","type":"core::integer::u256"}]},{"kind":"struct","name":"achievments::contract::contract::ApprovalForAll","type":"event","members":[{"kind":"key","name":"owner","type":"core::starknet::contract_address::ContractAddress"},{"kind":"key","name":"operator","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"approved","type":"core::bool"}]},{"kind":"enum","name":"achievments::contract::contract::Event","type":"event","variants":[{"kind":"nested","name":"Transfer","type":"achievments::contract::contract::Transfer"},{"kind":"nested","name":"Approval","type":"achievments::contract::contract::Approval"},{"kind":"nested","name":"ApprovalForAll","type":"achievments::contract::contract::ApprovalForAll"}]}]



    async def create_tnx_for_mint(self, sender: BaseAccount, eth: StarkToken, contract_address: int = None):
        if contract_address is None:
            contract_address = choice(self.contracts)

        contract = Contract(contract_address, self.ABI, sender.stark_native_account, cairo_version=1)
        price = (await handle_dangerous_request(contract.functions["get_price"].call, "can't get NFT price. Error", sender.stark_address))[0]
        call1 = eth.get_approve_call_wei(price, contract_address, sender)

        call2 = contract.functions["mint"].prepare_call()

        return [call1, call2]
    
    async def asd(self, sender):
        print(1)
        calls = []
        print(2)
        for address in self.contracts:
            print(3)
            contract = Contract(address, self.ABI, sender.stark_native_account, cairo_version=1)
            print(4)
            call2 = contract.functions["withdraw"].prepare_call()
            print(5)
            calls.append(call2)
        
        return calls
            
    
starkstars = StarkStars()