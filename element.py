from BaseClasses import *

class ElementMarket:

    async def get_token_id(self, sender: BaseAccount, collection: str):
        data = {"operationName":"AssetsListFromUser",
                "variables":{
                    "realtime":True,
                    "thirdStandards":["element-ex-v3"],
                    "sortAscending":False,
                    "sortBy":"RecentlyTransferred",
                    "ownerAddress":sender.formatted_hex_address,
                    "first":36,
                    "uiFlag":"COLLECTED",
                    "blockChains":[{"chain":"starknet","chainId":"0xaaee1"}],
                    "account":{
                        "address":sender.formatted_hex_address,
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
        "X-Viewer-Addr": sender.formatted_hex_address,
        "X-Viewer-Chainmid": '1001'
        }

        r = mod_requests.post("https://api.element.market/graphql?args=AssetsListFromUser", headers=headers, impersonate="chrome101", json=data)

        res = r.json()


    async def sell(self, sender: BaseAccount):
        price = int(0.228 *1e18)
        nft_contract = ""

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
                    "expiry_time": int(time.time()+3600),
                    "fees": [
                        {
                        "amount": str(int(price*0.02)),
                        "recipient": "0x0759b2c73ffc02e60168f478803dd0f4929cebeb68ffbd1dd188a72e82996622"
                        }
                    ],
                    "listing_time": int(c/1000-600),
                    "maker": sender.formatted_hex_address,
                    "nft_address": "0x00b719f69b00a008a797dc48585449730aa1c09901fdbac1bc94b3bdc287cf76",
                    "nft_amount": 1,
                    "nft_id": {
                        "high": "0x0",
                        "low": "0x818d"
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



        print(json.dumps(message,indent=3))
        b = "{"
        bc = "}"
        data = {
            "maker":sender.formatted_hex_address,
            "signature":[str(signature[0]),str(signature[1])],
            "exchange":"0x04d8bb956e6bd7a50fcb8b49d8e9fd8269cfadbeb73f457fd6d3fc1dff4b879e",
        "orders":[f"{b}\"order_type\":{message['order_type']},\"taker\":\"{message['taker']}\",\"listing_time\":{message['listing_time']},\"expiry_time\":{message['expiry_time']},\"salt\":\"{message['salt']}\",\"erc20_address\":\"{message['erc20_address']}\",\"erc20_amount\":\"{message['erc20_amount']}\",\"fees\":[{b}\"recipient\":\"{message['fees'][0]['recipient']}\",\"amount\":\"{message['fees'][0]['amount']}\"{bc}],\"nft_address\":\"{message['nft_address']}\",\"nft_id\":\"{message['nft_id']}\",\"nft_amount\":{message['nft_amount']},\"order_validator\":\"{message['order_validator']}\",\"counter\":\"{message['counter']}\"{bc}"],
            "chainMId":1001,
            "standard":"element-ex-v3"}
        
        print(data)
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
        "X-Api-Sign": "a61b4b1da3c229a72b141a07c32e78bf85946e601e93c8adba98309bedabacf6.6518.1696948802",
        "X-Viewer-Chainmid": '1001'
        }

        r = mod_requests.post("https://api.element.market/v3/orders/genericPostBatch", headers=headers, impersonate="chrome101", json=data)

        print(r.text)
        print(r.status_code)
        print(r.headers)
