from cfg import *


class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e

salt = 0x23563a33746bcf102244c26923ab5eea268d56c25f3fb686268adb8477df528
account_initialize_call_data = [0x23563a33746bcf102244c26923ab5eea268d56c25f3fb686268adb8477df528]

call_data = [
    0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
    0x2dd76e7ad84dbed81c314ffe5e7a7cacfb8f4836f01af4e913f275f89a3de1a,
    len(account_initialize_call_data),
    *account_initialize_call_data
]
       
address = compute_address(
    salt=salt,
    class_hash=class_hash,  
    constructor_calldata=call_data,
    deployer_address=0,
)

print(hex(address))