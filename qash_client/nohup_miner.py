from module.takaro_module import *
from module.char_color import Color
from sys import argv
from time import sleep

args = argv
error_log = False

if len(args) <= 1:
    print("Usage: nohup_miner.py <private_key> <error_log(true/false):option>")
    exit()
elif len(args) == 2:
    miner_wallet = Privatekey(args[1]).wallet()
else:
    miner_wallet = Privatekey(args[1]).wallet()
    if args[2] in ["true","True","TRUE"]:
        error_log = True


while True:
    try:
        transaction_task = Node_explorer.task()
        transaction_task.mine(miner_wallet,Node_explorer.previous_hash(),"qash nohup miner by h4ribote")
        transaction_task.post()
        print(f"{transaction_task.transaction_id} +{amount_format(transaction_task.fee_amount)}tak")
    except Exception as e:
        if error_log:
            print(f"{Color.RED}ERROR{Color.COLOR_DEFAULT}: {e}")
            sleep(5)
