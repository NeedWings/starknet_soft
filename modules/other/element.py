from modules.base_classes.base_account import BaseAccount
from starknet_py.contract import Contract
from curl_cffi import requests
from modules.utils.logger import logger
import time 
import random
import json

class ElementMarket:

    async def get_token_id(self, sender: BaseAccount):
        data = {"operationName":"AssetsListFromUser",
                "variables":{
                    "realtime":True,
                    "thirdStandards":["element-ex-v3"],
                    "sortAscending":False,
                    "sortBy":"RecentlyTransferred",
                    "ownerAddress":sender.stark_address,
                    "first":36,
                    "uiFlag":"COLLECTED",
                    "blockChains":[{"chain":"starknet","chainId":"0xaaee1"}],
                    "account":{
                        "address":sender.stark_address,
                        "blockChain":{
                            "chain":"starknet","chainId":"0xaaee1"
                        }
                    },
                    "constantWhenERC721":1
                },
                "query":"query AssetsListFromUser($before: String, $after: String, $first: Int, $last: Int, $querystring: String, $categorySlugs: [String!], $collectionSlugs: [String!], $sortBy: SearchSortBy, $sortAscending: Boolean, $toggles: [SearchToggle!], $ownerAddress: Address, $creatorAddress: Address, $blockChains: [BlockChainInput!], $paymentTokens: [String!], $priceFilter: PriceFilterInput, $stringTraits: [StringTraitInput!], $contractAliases: [String!], $thirdStandards: [String!], $uiFlag: SearchUIFlag, $account: IdentityInput, $constantWhenERC721: Int) {\n  search(\n    \n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    search: {querystring: $querystring, categorySlugs: $categorySlugs, collectionSlugs: $collectionSlugs, sortBy: $sortBy, sortAscending: $sortAscending, toggles: $toggles, ownerAddress: $ownerAddress, creatorAddress: $creatorAddress, blockChains: $blockChains, paymentTokens: $paymentTokens, priceFilter: $priceFilter, stringTraits: $stringTraits, contractAliases: $contractAliases, uiFlag: $uiFlag}\n  ) {\n    totalCount\n    edges {\n      cursor\n      node {\n        asset {\n          chain\n          chainId\n          contractAddress\n          tokenId\n          tokenType\n          name\n          imagePreviewUrl\n          animationUrl\n          rarityRank\n          isFavorite\n          ownedQuantity(viewer: $account, constantWhenERC721: $constantWhenERC721)\n          orderData(standards: $thirdStandards, account: $account) {\n            bestAsk {\n              ...BasicOrder\n            }\n            bestBid {\n              ...BasicOrder\n            }\n          }\n          assetEventData {\n            lastSale {\n              lastSaleDate\n              lastSalePrice\n              lastSalePriceUSD\n              lastSaleTokenContract {\n                name\n                address\n                icon\n                decimal\n                accuracy\n              }\n            }\n          }\n          marketStandards(account: $account) {\n            count\n            standard\n            floorPrice\n          }\n          collection {\n            name\n            isVerified\n            slug\n            imageUrl\n            royaltyAddress\n            royalty\n            royaltyFeeEnforced\n            contracts {\n              blockChain {\n                chain\n                chainId\n              }\n            }\n          }\n          suspiciousStatus\n          uri\n        }\n      }\n    }\n    pageInfo {\n      hasPreviousPage\n      hasNextPage\n      startCursor\n      endCursor\n    }\n  }\n}\n\nfragment BasicOrder on OrderV3Type {\n  __typename\n  chain\n  chainId\n  chainMId\n  expirationTime\n  listingTime\n  maker\n  taker\n  side\n  saleKind\n  paymentToken\n  quantity\n  priceBase\n  priceUSD\n  price\n  standard\n  contractAddress\n  tokenId\n  schema\n  extra\n  paymentTokenCoin {\n    name\n    address\n    icon\n    chain\n    chainId\n    decimal\n    accuracy\n  }\n}\n"}

        headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9",
        "Content-Type": "application/json",
        "sec-ch-ua": "\"Chromium\";v=\"117\", \"Not;A=Brand\";v=\"8\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "X-Api-Key": "zQbYj7RhC1VHIBdWU63ki5AJKXloamDT",
        "X-Api-Sign": "88f8b1f3a83d5a4ea795ff3c025f42d6c8e044f38df6e193441196db31cfe144.8578.1697618584",
        "X-Query-Args": "AssetsListFromUser",
        "X-Viewer-Addr": sender.stark_address,
        "X-Viewer-Chainmid": '1001'
        }

        r = requests.post("https://api.element.market/graphql?args=AssetsListFromUser", headers=headers, impersonate="chrome101", json=data)

        res = r.json()['data']['search']['edges']
        for i in res:
            if i['node']['asset']['name'] == "Quantum Leap":
                return int(i['node']['asset']['tokenId'])


    async def sell(self, sender: BaseAccount):
        token_id = await self.get_token_id(sender)
        if token_id is None:
            logger.info(f"[{sender.stark_address}] sold")
            return
        price = int(round(random.uniform(0.00391, 0.00400), 6)*1e18)
        #await self.approve_collection(sender)
        c = int(time.time()*1000)
        to_sign = {
            "domain": {
                "chainId": "SN_MAIN",
                "name": "element_exchange",
                "version": "1.1"
            },
            "message": {
                "order": {
                    "counter": "0",
                    "erc20_address": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
                    "erc20_amount": str(price),
                    "expiry_time": int(time.time()+30*24*3600),
                    "fees": [
                        {
                        "amount": str(int(price*0.02)),
                        "recipient": "0x0759b2c73ffc02e60168f478803dd0f4929cebeb68ffbd1dd188a72e82996622"
                        }
                    ],
                    "listing_time": int(c/1000-600),
                    "maker": sender.stark_address,
                    "nft_address": "0x00b719f69b00a008a797dc48585449730aa1c09901fdbac1bc94b3bdc287cf76",
                    "nft_amount": 1,
                    "nft_id": {
                        "high": "0x0",
                        "low": hex(token_id)
                    },
                    "order_type": 1,
                    "order_validator": "0x0",
                    "salt": str(c),
                    "taker": "0x0"
                }
            },
            "primaryType": "Message",
            "types": {
                "Fee": [
                {
                    "name": "recipient",
                    "type": "felt"
                },
                {
                    "name": "amount",
                    "type": "felt"
                }
                ],
                "Message": [
                {
                    "name": "order",
                    "type": "Order"
                }
                ],
                "Order": [
                {
                    "name": "order_type",
                    "type": "felt"
                },
                {
                    "name": "maker",
                    "type": "felt"
                },
                {
                    "name": "taker",
                    "type": "felt"
                },
                {
                    "name": "listing_time",
                    "type": "felt"
                },
                {
                    "name": "expiry_time",
                    "type": "felt"
                },
                {
                    "name": "salt",
                    "type": "felt"
                },
                {
                    "name": "erc20_address",
                    "type": "felt"
                },
                {
                    "name": "erc20_amount",
                    "type": "felt"
                },
                {
                    "name": "fees",
                    "type": "Fee*"
                },
                {
                    "name": "nft_address",
                    "type": "felt"
                },
                {
                    "name": "nft_id",
                    "type": "Uint256"
                },
                {
                    "name": "nft_amount",
                    "type": "felt"
                },
                {
                    "name": "order_validator",
                    "type": "felt"
                },
                {
                    "name": "counter",
                    "type": "felt"
                }
                ],
                "StarkNetDomain": [
                {
                    "name": "name",
                    "type": "felt"
                },
                {
                    "name": "version",
                    "type": "felt"
                },
                {
                    "name": "chainId",
                    "type": "felt"
                }
                ],
                "Uint256": [
                {
                    "name": "low",
                    "type": "felt"
                },
                {
                    "name": "high",
                    "type": "felt"
                }
                ]
            }
            }
        signature = sender.stark_native_account.sign_message(typed_data=to_sign)

        buff = to_sign["message"]["order"]

        buff["nft_id"] = int(buff["nft_id"]["low"], 16)

        message = {
            "order_type": buff["order_type"],
            "taker": buff["taker"],
            "listing_time":buff["listing_time"],
            "expiry_time": buff["expiry_time"],
            "salt": buff["salt"],
            "erc20_address": buff["erc20_address"],
            "erc20_amount": buff["erc20_amount"],
            "fees": [
                {
                    "recipient":buff["fees"][0]["recipient"],
                    "amount":buff["fees"][0]["amount"]
                }
            ],
            "nft_address": buff["nft_address"],
            "nft_id": buff["nft_id"],
            "nft_amount": buff["nft_amount"],
            "order_validator": buff["order_validator"],
            "counter": buff["counter"]
        }



        b = "{"
        bc = "}"
        data = {
            "maker":sender.stark_address,
            "signature":[str(signature[0]),str(signature[1])],
            "exchange":"0x04d8bb956e6bd7a50fcb8b49d8e9fd8269cfadbeb73f457fd6d3fc1dff4b879e",
        "orders":[f"{b}\"order_type\":{message['order_type']},\"taker\":\"{message['taker']}\",\"listing_time\":{message['listing_time']},\"expiry_time\":{message['expiry_time']},\"salt\":\"{message['salt']}\",\"erc20_address\":\"{message['erc20_address']}\",\"erc20_amount\":\"{message['erc20_amount']}\",\"fees\":[{b}\"recipient\":\"{message['fees'][0]['recipient']}\",\"amount\":\"{message['fees'][0]['amount']}\"{bc}],\"nft_address\":\"{message['nft_address']}\",\"nft_id\":\"{message['nft_id']}\",\"nft_amount\":{message['nft_amount']},\"order_validator\":\"{message['order_validator']}\",\"counter\":\"{message['counter']}\"{bc}"],
            "chainMId":1001,
            "standard":"element-ex-v3"}

        headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9",
        "Content-Type": "application/json",
        "sec-ch-ua": "\"Chromium\";v=\"117\", \"Not;A=Brand\";v=\"8\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "X-Api-Key": "zQbYj7RhC1VHIBdWU63ki5AJKXloamDT",
        "X-Api-Sign": "0dccb5745d68b7b3b15911015569eed58606dc0b68b9eeb194ea4eba7399fdd8.1937.1704121802",
        "X-Viewer-Chainmid": '1001'
        }

        r = requests.post("https://api.element.market/v3/orders/genericPostBatch", headers=headers, impersonate="chrome101", json=data)

        logger.info(f"[{sender.stark_address}] {r.text}")

    async def approve_collection(self, sender: BaseAccount):
        contract = Contract(0x00b719f69b00a008a797dc48585449730aa1c09901fdbac1bc94b3bdc287cf76, abi=[
  {
    "members": [
      {
        "name": "low",
        "offset": 0,
        "type": "felt"
      },
      {
        "name": "high",
        "offset": 1,
        "type": "felt"
      }
    ],
    "name": "Uint256",
    "size": 2,
    "type": "struct"
  },
  {
    "data": [
      {
        "name": "previousOwner",
        "type": "felt"
      },
      {
        "name": "newOwner",
        "type": "felt"
      }
    ],
    "keys": [],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "data": [
      {
        "name": "from_",
        "type": "felt"
      },
      {
        "name": "to",
        "type": "felt"
      },
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "keys": [],
    "name": "Transfer",
    "type": "event"
  },
  {
    "data": [
      {
        "name": "owner",
        "type": "felt"
      },
      {
        "name": "approved",
        "type": "felt"
      },
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "keys": [],
    "name": "Approval",
    "type": "event"
  },
  {
    "data": [
      {
        "name": "owner",
        "type": "felt"
      },
      {
        "name": "operator",
        "type": "felt"
      },
      {
        "name": "approved",
        "type": "felt"
      }
    ],
    "keys": [],
    "name": "ApprovalForAll",
    "type": "event"
  },
  {
    "data": [
      {
        "name": "implementation",
        "type": "felt"
      }
    ],
    "keys": [],
    "name": "Upgraded",
    "type": "event"
  },
  {
    "data": [
      {
        "name": "previousAdmin",
        "type": "felt"
      },
      {
        "name": "newAdmin",
        "type": "felt"
      }
    ],
    "keys": [],
    "name": "AdminChanged",
    "type": "event"
  },
  {
    "inputs": [
      {
        "name": "name",
        "type": "felt"
      },
      {
        "name": "symbol",
        "type": "felt"
      },
      {
        "name": "owner",
        "type": "felt"
      }
    ],
    "name": "initializer",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalSupply",
    "outputs": [
      {
        "name": "totalSupply",
        "type": "Uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "index",
        "type": "Uint256"
      }
    ],
    "name": "tokenByIndex",
    "outputs": [
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "owner",
        "type": "felt"
      },
      {
        "name": "index",
        "type": "Uint256"
      }
    ],
    "name": "tokenOfOwnerByIndex",
    "outputs": [
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "interfaceId",
        "type": "felt"
      }
    ],
    "name": "supportsInterface",
    "outputs": [
      {
        "name": "success",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "name",
    "outputs": [
      {
        "name": "name",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "symbol",
    "outputs": [
      {
        "name": "symbol",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "mintPhase",
    "outputs": [
      {
        "name": "phase",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "owner",
        "type": "felt"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "name": "balance",
        "type": "Uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "name": "ownerOf",
    "outputs": [
      {
        "name": "owner",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "name": "getApproved",
    "outputs": [
      {
        "name": "approved",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "owner",
        "type": "felt"
      },
      {
        "name": "operator",
        "type": "felt"
      }
    ],
    "name": "isApprovedForAll",
    "outputs": [
      {
        "name": "approved",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "name": "tokenURI",
    "outputs": [
      {
        "name": "uri_len",
        "type": "felt"
      },
      {
        "name": "uri",
        "type": "felt*"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "name": "owner",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "address",
        "type": "felt"
      }
    ],
    "name": "hasMinted",
    "outputs": [
      {
        "name": "hasMinted",
        "type": "felt"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "to",
        "type": "felt"
      },
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "name": "approve",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "phase",
        "type": "felt"
      }
    ],
    "name": "setMintPhase",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "operator",
        "type": "felt"
      },
      {
        "name": "approved",
        "type": "felt"
      }
    ],
    "name": "setApprovalForAll",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "from_",
        "type": "felt"
      },
      {
        "name": "to",
        "type": "felt"
      },
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "name": "transferFrom",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "from_",
        "type": "felt"
      },
      {
        "name": "to",
        "type": "felt"
      },
      {
        "name": "tokenId",
        "type": "Uint256"
      },
      {
        "name": "data_len",
        "type": "felt"
      },
      {
        "name": "data",
        "type": "felt*"
      }
    ],
    "name": "safeTransferFrom",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "to",
        "type": "felt"
      }
    ],
    "name": "mint",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "to",
        "type": "felt"
      }
    ],
    "name": "mintPublic",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "tokenId",
        "type": "Uint256"
      }
    ],
    "name": "burn",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "newOwner",
        "type": "felt"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "type": "function"
  },
  {
    "inputs": [
      {
        "name": "uri_len",
        "type": "felt"
      },
      {
        "name": "uri",
        "type": "felt*"
      }
    ],
    "name": "setTokenUri",
    "outputs": [],
    "type": "function"
  }
], provider=sender.stark_native_account)
        call = contract.functions["setApprovalForAll"].prepare(0x04d8bb956e6bd7a50fcb8b49d8e9fd8269cfadbeb73f457fd6d3fc1dff4b879e, 1)

        await sender.send_txn_starknet([call])


element_market = ElementMarket()