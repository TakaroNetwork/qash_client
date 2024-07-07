from module.takaro_module import *
from module.char_color import Color
from pandas import DataFrame
from decimal import Decimal
import json
import re
import time
from traceback import TracebackException, StackSummary

CLIENT_VERSION = "1.0"
FEE_CURRENCY:Currency = Currency("5ycR960r5pR","takaro","tak",NETWORK_ADMIN_address,80241013)
RED_ERROR_STR = f"{Color.RED}Error{Color.COLOR_DEFAULT}: "

def bool_color(var:bool):
    if var == True:
        return f"{Color.CYAN}True{Color.COLOR_DEFAULT}"
    else:
        return f"{Color.RED}False{Color.COLOR_DEFAULT}"

def validate_char(input_string):
    return re.sub(r'[^a-zA-Z0-9]', '', input_string)

def load_data(file_name:str):
    path = 'data/' + file_name
    with open(path) as f:
        file = json.load(f)
    return file

def write_data(file_name:str,data:dict):
    path = 'data/' + file_name
    with open(path, 'w') as f:
        json.dump(data, f,indent=-1)

class helps:
    # CommandName = [description, arguments]
    transfer = ["対象のアドレスに送金します",
                "<SelfMining>","マイニングをしてから取引を送信します(=false)"]
    balance = ["ウォレットの残高を表示します",
               "<address>","対象のウォレットのアドレス(=現在のウォレットアドレス)"]
    explorer = ["取引の詳細な検索を行います",
                "<SubCommand>","検索条件の設定[options,set]"]
    validate = ["ネットワーク上での取引の履歴を検証します",
                "[ValidateMode]","検証モードを指定  allで全取引、整数値で範囲を指定"]
    
    commands:dict[str,list[str]] = {
            "transfer":transfer,
            "balance":balance,
            "explorer":explorer,
            "validate":validate
            }
    def show(command:str):
        if command in helps.commands:
            descriptions = helps.commands[command]
            i = 3
            print(f" {command} - {descriptions[0]}")
            command_example = f"   {command}"
            print_lines = ["   []: 必要な引数 | <>: 任意の引数\n"]

            while True:
                if len(descriptions) >= i:
                    command_example += f" {descriptions[i-1]}"
                    print_lines.append(f"   {descriptions[i-1]} {descriptions[i]}")
                else:
                    break
                i += 2
            
            print(command_example)
            for lines in print_lines:
                print(lines)
        else:
            print("コマンドが存在しません")
            


class wallet_json:
    def add(new_wallet_name:str,wallet:Wallet):
        wallets = load_data('wallet.json')
        wallets[new_wallet_name] = {"address":wallet.address,"private_key":wallet.private_key}
        write_data('wallet.json',wallets)
    
    def load():
        wallets:dict[str,Wallet] = {}
        wallets_dict:dict = load_data('wallet.json')
        for wallet_name in wallets_dict.keys():
            wallet_info:dict = wallets_dict[wallet_name]
            wallets[wallet_name] = Privatekey(wallet_info['private_key']).wallet()
        return wallets

    def remove(wallet_name):
        wallets = load_data('wallet.json')
        del wallets[wallet_name]
        write_data('wallet.json',wallets)

class currency_json:
    def add(currency:Currency):
        currencies = load_data('currency.json')
        currencies[currency.currency_id] = {
            "currency_id":currency.currency_id,
            "name":currency.name,
            "symbol":currency.symbol,
            "admin":currency.admin,
            "nonce":currency.nonce
            }
        write_data('currency.json',currencies)
    
    def load():
        currencies:dict[str,Currency] = {}
        currencies_dict:dict = load_data('currency.json')
        for currency_id in currencies_dict.keys():
            info = currencies_dict[currency_id]
            currencies[currency_id] = Currency(currency_id,info['name'],info['symbol'],info['admin'],info['nonce'])
        return currencies
    
    def remove(currency_id):
        currencies_dict = load_data('currency.json')
        del currencies_dict[currency_id]
        write_data('currency.json',currencies_dict)
    
class transaction_json:
    def load():
        transactions:list[dict] = load_data('transaction.json')
        return transactions
    
    def convert(transaction:dict|list|Transaction) -> Transaction|list|dict:
        if type(transaction) == dict:
            converted:Transaction = Transaction.from_dict(transaction)
        elif type(transaction) == list:
            converted:list[Transaction] = []
            for trnsct in transaction:
                converted.append(Transaction.from_dict(trnsct))
        elif type(transaction) == Transaction:
            converted:dict = {}
            converted = transaction.to_dict()
        else:
            raise TypeError()
        
        return converted
    
    def sync():
        transactions:list[dict] = load_data('transaction.json')
        while True:
            next_index_id = len(transactions)
            response:list[dict] = Api.get('/explorer/transaction',{'index_id_from':next_index_id})
            if response:
                response.reverse()
                transactions += response
            else:
                break
        write_data('transaction.json',transactions)
        return transactions

class explorer:
    def option(transaction_id:str="",index_id:str="",index_id_from:str="",address:str="",source:str="",dest:str="",currency_id:str="",miner:str=""):
        explorer_option = {
            "transaction_id":transaction_id,
            "index_id":index_id,
            "index_id_from":index_id_from,
            "address":address,
            "source":source,
            "dest":dest,
            "currency_id":currency_id,
            "miner":miner
        }
        return explorer_option
    
    def explorer(transactions:list,options:dict):
        conditions:str = ""
        result:list[dict] = []
        opt = False

        if options['transaction_id']:
            conditions = explorer.explorer_conditions(conditions, 'transaction_id', options['transaction_id'])
            opt = True
        if options['index_id']:
            conditions = explorer.explorer_conditions(conditions, 'index_id', options['index_id'])
            opt = True
        if options['index_id_from']:
            conditions = explorer.explorer_conditions_id_from(conditions, options['index_id_from'])
            opt = True
        if options['address']:
            conditions = explorer.explorer_conditions_address(conditions, options['address'])
            opt = True
        if options['source']:
            conditions = explorer.explorer_conditions(conditions, 'source', options['source'])
            opt = True
        if options['dest']:
            conditions = explorer.explorer_conditions(conditions, 'dest', options['dest'])
            opt = True
        if options['currency_id']:
            conditions = explorer.explorer_conditions(conditions, 'currency_id', options['currency_id'])
            opt = True
        if options['miner']:
            conditions = explorer.explorer_conditions(conditions, 'miner', options['miner'])
            opt = True

        if opt:
            for transaction in transactions:
                exec(f'{conditions}: result.append(transaction)')
        else:
            result = transactions
        
        return result

    def explorer_conditions(conditions, condition_name, var):
        if conditions == "":
            conditions = f"if transaction['{condition_name}'] == '{var}'"
        else:
            conditions += f" and transaction['{condition_name}'] == '{var}'"
        return conditions

    def explorer_conditions_id_from(conditions, index_id):
        if conditions == "":
            conditions = f"if transaction['index_id'] >= '{index_id}'"
        else:
            conditions += f" and transaction['index_id'] >= '{index_id}'"
        return conditions

    def explorer_conditions_address(conditions, address):
        if conditions == "":
            conditions = f"if (transaction['source'] == '{address}' or transaction['dest'] == '{address}')"
        else:
            conditions += f" and (transaction['source'] == '{address}' or transaction['dest'] == '{address}')"
        return conditions
    
    def balance(address:str,transactions:list,currency_id:str = None) -> dict[str,int]:
        wallet_balance:dict[str,int] = {}
        if currency_id:
            wallet_balance[currency_id] = 0
        # deposit
        exp_transactions = (explorer.explorer(transactions,explorer.option(dest=address)))
        for transaction in exp_transactions:
            currency_id = transaction['currency_id']
            amount = int(transaction['amount'])
            if currency_id in wallet_balance:
                wallet_balance[currency_id] += amount
            else:
                wallet_balance[currency_id] = amount
        # withdraw
        if address != NETWORK_ADMIN_address:
            exp_transactions = (explorer.explorer(transactions,explorer.option(source=address)))
            for transaction in exp_transactions:
                currency_id = transaction['currency_id']
                amount = int(transaction['amount'])
                fee_amount = int(transaction['fee_amount'])
                if currency_id in wallet_balance:
                    wallet_balance[currency_id] += -amount
                else:
                    wallet_balance[currency_id] = -amount
                if FEE_CURRENCY_id in wallet_balance:
                    wallet_balance[FEE_CURRENCY_id] += -fee_amount
                else:
                    wallet_balance[FEE_CURRENCY_id] = -fee_amount
        # mining reward
        exp_transactions = (explorer.explorer(transactions,explorer.option(miner=address)))
        for transaction in exp_transactions:
            fee_amount = int(transaction['fee_amount'])
            if currency_id in wallet_balance:
                wallet_balance[currency_id] += fee_amount
            else:
                wallet_balance[currency_id] = fee_amount

        return wallet_balance

def main():
    explorer_option = explorer.option()
    currencies = currency_json.load()
    wallets = wallet_json.load()
    try:
        transaction_json.sync()
    except Exception as e:
        print(f"{Color.RED}Warning{Color.COLOR_DEFAULT}: Unable to sync transaction({e})")
    transactions = transaction_json.load()

    print("<-----wallet list----->")
    i = 0
    for wallet__name in wallets.keys():
        for__wallet = wallets[wallet__name]
        wallet__balance = explorer.balance(for__wallet.address,transactions,FEE_CURRENCY.currency_id)
        print(f"[{i}] {wallet__name} ({Color.YELLOW}{for__wallet.address}{Color.COLOR_DEFAULT}): {amount_format(wallet__balance[FEE_CURRENCY.currency_id])}tak")
        i += 1
    print(f"[{i}] generate new wallet")
    print(f"[{i+1}] import with private key")

    while True:
        select_id = input("Select wallet number: ")
        try:
            select_id = int(select_id)
            if select_id > i+1:
                raise ValueError()
            if select_id == i:
                selected_wallet_name = input("New wallet name: ")
                wallet = Wallet.generate()
                wallet_json.add(selected_wallet_name,wallet)
            elif select_id == i+1:
                selected_wallet_name = input("Wallet name: ")
                wallet = Privatekey(input("private key: ")).wallet()
                wallet_json.add(selected_wallet_name,wallet)
            else:
                selected_wallet_name = list(wallets)[select_id]
                wallet = wallets[selected_wallet_name]
            break
        except:
            print(RED_ERROR_STR,"Invalid input")
    print(f"\nSelected wallet({selected_wallet_name}):\n  address: {Color.YELLOW}{wallet.address}{Color.COLOR_DEFAULT}\n"
          f"  public_key: {wallet.public_key[:6]}......{wallet.public_key[-6:]}\n  private_key: ***************\n\n")

    while True:
        try:
            command = input('\n$ ')
            args = command.split(' ')
            cmd = args[0]
            if cmd == "transfer":
                self_mining = True
                if len(args) >= 2:
                    if args[1] in ["true","True","TRUE","1"]:
                        self_mining = True
                    elif args[1] in ["false","False","FALSE","0"]:
                        self_mining = False
                while True:
                    transfer_dest = input("\n送信先アドレス: ")
                    if transfer_dest:
                        transfer_dest = Address(transfer_dest)
                        break
                    else:
                        print(RED_ERROR_STR,"送信先を空にすることはできません")
                i = 0
                currency_ids_list = []
                balance_response = explorer.balance(wallet.address,transactions)
                for currency in currencies.values():
                    currency_ids_list.append(currency.currency_id)
                    print(f"[{i}] {currency.name}({currency.symbol}) [{currency.currency_id}]: ",end="")
                    if currency.currency_id in balance_response:
                        print(f"{amount_format(balance_response[currency.currency_id])}{currency.symbol}")
                    else:
                        print(f"0{currency.symbol}")
                    i += 1
                while True:
                    try:
                        selected_currency = int(input(f"\n送信する通貨を選択(0~{i-1}): "))
                        transfer_currency = currencies[currency_ids_list[selected_currency]]
                        break
                    except:
                        print(RED_ERROR_STR,"範囲内の数値を入力してください")
                
                while True:
                    try:
                        transfer_amount = int(Decimal(input("\n送信する数量: "))*1000000)
                        if transfer_amount <= 0:
                            raise Exception
                        break
                    except:
                        print(RED_ERROR_STR,"範囲内の数値を入力してください")
                
                while True:
                    try:
                        transfer_fee_amount = int(Decimal(input("\n手数料(takaro): "))*1000000)
                        if transfer_fee_amount < 0:
                            raise Exception
                        break
                    except:
                        print(RED_ERROR_STR,"範囲内の数値を入力してください")
                
                while True:
                    transfer_comment = input("\nコメント: ")
                    if len(transfer_comment) > 190:
                        print(RED_ERROR_STR,"コメントは190字以下")
                    else:
                        break
                
                print(f"\n"
                      f"送信元: {wallet.address}\n"
                      f"送信量: {transfer_amount}{transfer_currency.symbol}\n"
                      f"手数料: {transfer_fee_amount}tak\n"
                      f"送信先: {transfer_dest.address}\n")
                transfer_confirm = input(f"取引内容を確認し、正しければ'confirm'と入力してください(confirm以外の入力でキャンセル)\n\n     Enter here:{Color.YELLOW} ")
                print(Color.COLOR_DEFAULT)
                if transfer_confirm in ["confirm","Confirm","CONFIRM"]:
                    transfer_transaction = Transaction()
                    transfer_transaction.create(wallet,transfer_dest,transfer_amount,transfer_currency,transfer_fee_amount,transfer_comment)
                    if self_mining:
                        input("Enterを押すとマイニングが開始されます")
                        transfer_transaction.mine(wallet,Node_explorer.previous_hash(),"qash_client made by h4ribote")
                        transfer_transaction.post()
                        print("完了しました\n取引id: ",transfer_transaction.transaction_id)
                    else:
                        transfer_transaction.post_task()
                        print("送信しました\n取引id: ",transfer_transaction.transaction_id)
            
            if cmd == "balance":
                if len(args) >= 2:
                    balance_address = Address(args[1])
                else:
                    balance_address = wallet.Address
                
                balance_response = explorer.balance(balance_address,transactions)
                if balance_response:
                    for balance_cid in balance_response.keys():
                        balance_currency = currencies[balance_cid]
                        print(f"{balance_currency.name}({balance_currency.currency_id}): "
                              f"{amount_format(balance_response[balance_cid])}{balance_currency.symbol}")
                else:
                    print("ウォレットは空です")
            
            elif cmd == "exit":
                exit()
            try:
                transactions = transaction_json.sync()
            except Exception as e:
                print(e)
            
        except Exception as e:
            if str(e) == "list index out of range":
                print("引数が不足しています")
            else:
                tb = TracebackException.from_exception(e)
                caller = None
                for stack in tb.stack:
                    caller = stack
                summary = StackSummary.from_list([caller])
                print(e)
                print(''.join(summary.format()))

if __name__ == "__main__":
    main()
