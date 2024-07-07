__author__  = "h4ribote"
__email__   = "contact@h4ribote.net"
__version__ = '1.0'


import requests
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import hashlib
from decimal import Decimal


NODE_URL:str = "https://takaro.h4ribote.net/api/v0"
NETWORK_ADMIN_address:str = "XXXXXXUAsfeKpxUtN7kN52lv1wT4s0pxbqCgzybLqme"
FEE_CURRENCY_id:str = "5ycR960r5pR"


class Api:
    @staticmethod
    def post(path, data):
        try:
            response = requests.post(NODE_URL + path, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception(f"{response.status_code} {response.text}")
        except Exception as e:
            raise Exception(e)
        return response.json()

    @staticmethod
    def get(path, params=None):
        try:
            response = requests.get(NODE_URL + path, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception(f"{response.status_code} {response.json()['message']}: {response.json()['datail']}")
        except Exception as e:
            raise Exception(e)
        return response.json()

    @staticmethod
    def put(path, data, headers):
        try:
            response = requests.put(NODE_URL + path, json=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception(f"{response.status_code} {response.json()['message']}: {response.json()['datail']}")
        except Exception as e:
            raise Exception(e)
        return response.json()

class Node_explorer:
    def transaction(transaction_id:str = "",index_id:str = "",index_id_from:str = "",address:str = "",source:str = "",dest:str = "",currency_id:str = "",miner:str = "") -> list:
        """
        return {'index_id': Transaction}
        """
        transactions:list[Transaction] = []
        params = {'transaction_id':transaction_id,'index_id':index_id,'index_id_from':index_id_from,
                  'address':address,'source':source,'dest':dest,'currency_id':currency_id,'miner':miner}
        api_response = Api.get("/explorer/transaction",params)
        for transaction in api_response:
            trsct = Transaction().from_dict(transaction)
            transactions.append(trsct)
        return transactions
    
    def balance(currency_id:str = "",address:str = "") -> list:
        """
        return [{'address': str, 'currency_id': str, 'amount': int}]
        """
        explorer_balance:list[dict[str,any]] = []
        response = Api.get("/explorer/balance",{'currency_id':currency_id,'address':address})
        for balance in response:
            explorer_balance.append({'address':balance['address'],'currency_id':balance['currency_id'],'amount':int(balance['amount'])})
        return response
    
    def currency(currency_id:str = "",name:str = "",unit:str = "",admin:str = "") -> list:
        """
        return list[Currency]
        """
        currencies = []
        params = {'currency_id':currency_id,'name':name,'unit':unit,'admin':admin}
        response = Api.get("/explorer/currency",params)
        for currency in response:
            currencies.append(Currency(currency['currency_id'],currency['name'],currency['symbol'],currency['admin'],currency['nonce']))
        
        return currencies
    
    def task():
        response = Api.get("/explorer/task")
        if response:
            task = Transaction().from_dict(response)
            return task
        else:
            raise Exception("No task available")
    
    def previous_hash() -> str:
        response = Api.get("/explorer/previous_hash")
        previous_hash = response['hash']
        return previous_hash

class Signature:
    def __init__(self,hex_sign:str):
        self.signature:str = hex_sign
        self.str:str = hex_sign

class Privatekey:
    def __init__(self,hex_private_key:str):
        self.private_key:str = hex_private_key
        self.str:str = hex_private_key
    
    def __str__(self) -> str:
        return self.private_key
    
    def __repr__(self) -> str:
        return f"Privatekey(******)"
    
    def wallet(self):
        wallet = Wallet()
        wallet.private_key = self.private_key
        wallet.Privatekey = Privatekey(self.private_key)
        private = SigningKey.from_string(bytes.fromhex(self.private_key), curve=SECP256k1)
        hex_public_key = private.verifying_key.to_string().hex()
        wallet.public_key = hex_public_key
        wallet.Publickey = Publickey(hex_public_key)
        public_hash = hashlib.sha256(bytes.fromhex(hex_public_key)).hexdigest()
        wallet.address = decimal_to_base62(int(public_hash,16))
        wallet.Address = Address(decimal_to_base62(int(public_hash,16)))
        return wallet
    

class Publickey:
    def __init__(self,hex_public_key:str):
        self.public_key:str = hex_public_key
        self.str:str = hex_public_key
    
    def __str__(self) -> str:
        return self.public_key
    
    def __repr__(self) -> str:
        return f"Publickey({self.public_key[:4]}....{self.public_key[-4:]})"
    
    def verify_sign(self,hex_data:str,signature:Signature) -> bool:
        public_key = VerifyingKey.from_string(bytes.fromhex(self.public_key),curve=SECP256k1)
        sign_data = bytes.fromhex(signature.signature)
        try:
            public_key.verify(sign_data,bytes.fromhex(hex_data))
            return True
        except:
            return False
    
    def wallet(self):
        wallet = Wallet()
        wallet.public_key = self.public_key
        wallet.Publickey = Publickey(self.public_key)
        public_hash = hashlib.sha256(bytes.fromhex(self.public_key)).hexdigest()
        wallet.address = decimal_to_base62(int(public_hash,16))
        wallet.Address = Address(decimal_to_base62(int(public_hash,16)))
        return wallet

class Address:
    def __init__(self,address:str):
        self.address:str = address
        self.str:str = address
    
    def wallet(self):
        wallet = Wallet()
        wallet.address = self.address
        return wallet
    
    def __str__(self) -> str:
        return self.address
    
    def __repr__(self) -> str:
        return f"Address({self.address})"

class Wallet:
    def __init__(self):
        self.private_key:str
        self.Privatekey:Privatekey
        self.public_key:str
        self.Publickey:Publickey
        self.address:str
        self.Address:Address
    
    def __str__(self) -> str:
        return self.address
    
    def __repr__(self) -> str:
        return f"Wallet(address={self.address},public={self.public_key[:4]}....{self.public_key[-4:]},private=******)"

    def generate():
        private_key = Privatekey(SigningKey.generate(curve=SECP256k1).to_string().hex())
        new_wallet = private_key.wallet()
        return new_wallet

    def balance(self,currency_id:str = None) -> dict[str,int]:
        """
        return {'currency_id': amount}
        """
        wallet_balance:dict[str,int] = {}
        if currency_id:
            wallet_balance[currency_id] = 0
        response = Api.get("/explorer/balance",{'address':self.address})
        for balance in response:
            wallet_balance[balance['currency_id']] = int(balance['amount'])
        return wallet_balance
    
    def sign(self,hex_data:str) -> Signature:
        sign_private_key = SigningKey.from_string(bytes.fromhex(self.private_key), curve=SECP256k1)
        return Signature(sign_private_key.sign(bytes.fromhex(hex_data)).hex())
    
    def verify_sign(self,hex_data:str,signature:Signature) -> bool:
        public_key = VerifyingKey.from_string(bytes.fromhex(self.public_key),curve=SECP256k1)
        sign_data = bytes.fromhex(signature.signature)
        try:
            public_key.verify(sign_data,bytes.fromhex(hex_data))
            return True
        except:
            return False

class Currency:
    def __init__(self,currency_id:str = None,name:str = None,symbol:str = None,admin:Address = None,nonce:int = None):
        self.currency_id:str = currency_id
        self.name:str = name
        self.symbol:str = symbol
        self.admin:Address = admin
        self.nonce:int = nonce
    
    def __str__(self) -> str:
        return self.currency_id
    
    def __repr__(self) -> str:
        return f"Currency(id={self.currency_id},name={self.name},symbol={self.symbol},admin={self.admin.address})"
    
    def create(name:str,symbol:str,admin:Address,difficulty:int=8):
        currency_data = f"{name}{symbol}{admin.str}"
        nonce = 0
        while True:
            data = f"{currency_data}{nonce}"
            hash_result = hashlib.sha256(data.encode()).hexdigest()
            if hash_result.startswith('0' * difficulty):
                break
            nonce += 1
        currency_hex = hash_result[-16:]
        currency_id = decimal_to_base62(int(currency_hex,16))
        new_currency = Currency()
        new_currency.currency_id = currency_id
        new_currency.name = name
        new_currency.symbol = symbol
        new_currency.admin = admin
        new_currency.nonce = nonce

        return new_currency
    
    def verify(self,difficulty:int=8) -> bool:
        try:
            currency_data = f"{self.name}{self.symbol}{self.admin.str}"
            data = f"{currency_data}{self.nonce}"
            hash_result = hashlib.sha256(data.encode()).hexdigest()
            currency_hex = hash_result[-16:]
            currency_id = decimal_to_base62(int(currency_hex,16))
            if (hash_result.startswith('0' * difficulty)) and (self.currency_id == currency_id):
                return True
            else:
                return False
        except:
            return False
    
    def info(self) -> dict:
        """
        return {'total_holder':int,'total_issued':int}
        """
        response = Api.get("/explorer/balance",{'currency_id':self.currency_id})
        total_issued = 0
        total_holder = len(response)
        transactions = Node_explorer.transaction(currency_id = self.currency_id, source = NETWORK_ADMIN_address)
        for trsct in transactions:
            total_issued += int(trsct['amount'])

        return {'total_holder':total_holder,'total_issued':total_issued}

class Transaction:
    def __init__(self, transaction_id:str = None, index_id:int = None,
                 signature:Signature = None, public_key:Publickey = None, previous_hash:str = None, source:Address = None, dest:Address = None,
                 amount:int = None, currency:Currency = None, fee_amount:int = None, comment:str = None, nonce:int = None,
                 miner:Address = None, miner_comment:str = None, miner_public_key:Publickey = None, miner_signature:Signature = None) -> None:
        self.transaction_id:str = transaction_id
        self.index_id:int = index_id
        self.signature:Signature = signature
        self.public_key:Publickey = public_key
        self.previous_hash:str = previous_hash
        self.source:Address = source
        self.dest:Address = dest
        self.amount:int = amount
        self.currency:Currency = currency
        self.fee_amount:int = fee_amount
        self.comment:str = comment
        self.nonce:int = nonce
        self.miner:Address = miner
        self.miner_comment:str = miner_comment
        self.miner_public_key:Publickey = miner_public_key
        self.miner_signature:Signature = miner_signature
    
    def create(self, wallet:Wallet, dest:Address, amount:int, currency:Currency, fee_amount:int, comment:str, indent:int=0) -> None:
        hex_data = hashlib.sha256(f"{wallet.address}{dest.address}{amount}{currency.currency_id}{fee_amount}{comment}".encode()).hexdigest()
        self.signature = wallet.sign(hex_data)
        self.public_key = wallet.Publickey
        self.source = wallet.Address
        self.dest = dest
        self.amount = amount
        self.currency = currency
        self.fee_amount = fee_amount
        self.comment = comment
        self.transaction_id = self.signature.str[-32:]
    
    def from_dict(transaction_dict: dict):
        transaction = Transaction()
        transaction.transaction_id = transaction_dict.get('transaction_id', None)
        transaction.index_id = int(transaction_dict.get('index_id', 0))
        transaction.signature = Signature(transaction_dict.get('signature', None))
        transaction.public_key = Publickey(transaction_dict.get('public_key', None))
        transaction.previous_hash = transaction_dict.get('previous_hash', None)
        transaction.source = Address(transaction_dict.get('source', None))
        transaction.dest = Address(transaction_dict.get('dest', None))
        transaction.amount = int(transaction_dict.get('amount', 0))
        transaction.currency = Currency(transaction_dict.get('currency', None))
        transaction.fee_amount = int(transaction_dict.get('fee_amount', 0))
        transaction.comment = transaction_dict.get('comment', None)
        transaction.nonce = int(transaction_dict.get('nonce', 0))
        transaction.miner = Address(transaction_dict.get('miner', None))
        transaction.miner_comment = transaction_dict.get('miner_comment', None)
        transaction.miner_public_key = Publickey(transaction_dict.get('miner_public_key', None))
        transaction.miner_signature = Signature(transaction_dict.get('miner_signature', None))
        return transaction
    
    def to_dict(self) -> dict:
        dict_data = {
            'transaction_id': self.transaction_id,
            'signature': self.signature.signature,
            'public_key': self.public_key.public_key,
            'previous_hash': self.previous_hash,
            'source': self.source.address,
            'dest': self.dest.address,
            'amount': self.amount,
            'currency_id': self.currency.currency_id,
            'fee_amount': self.fee_amount,
            'comment': self.comment,
            'nonce': self.nonce,
            'miner': self.miner.address,
            'miner_comment': self.miner_comment,
            'miner_public_key': self.miner_public_key.public_key,
            'miner_signature': self.miner_signature.signature
        }

        return dict_data
    
    def post(self):
        post_data = {
            'transaction_id': self.transaction_id,
            'signature': self.signature.signature,
            'public_key': self.public_key.public_key,
            'previous_hash': self.previous_hash,
            'source': self.source.address,
            'dest': self.dest.address,
            'amount': self.amount,
            'currency_id': self.currency.currency_id,
            'fee_amount': self.fee_amount,
            'comment': self.comment,
            'nonce': self.nonce,
            'miner': self.miner.address,
            'miner_comment': self.miner_comment,
            'miner_public_key': self.miner_public_key.public_key,
            'miner_signature': self.miner_signature.signature
        }

        response = Api.post("/post/transaction", post_data)
    
    def post_task(self):
        post_data = {
            'transaction_id': self.transaction_id,
            'signature': self.signature.signature,
            'public_key': self.public_key.public_key,
            'source': self.source.address,
            'dest': self.dest.address,
            'amount': self.amount,
            'currency_id': self.currency.currency_id,
            'fee_amount': self.fee_amount,
            'comment': self.comment
        }

        response = Api.post("/post/task", post_data)
    
    def transaction_hash(self) -> str:
        transaction_data = (f"{self.transaction_id}{self.index_id}{self.signature.signature}"
                            f"{self.public_key.public_key}{self.previous_hash}"
                            f"{self.source.address}{self.dest.address}{self.amount}{self.currency.currency_id}"
                            f"{self.fee_amount}{self.comment}{self.nonce}{self.miner.address}{self.miner_comment}"
                            f"{self.miner_public_key.public_key}{self.miner_signature.signature}")
        
        return hashlib.sha256(transaction_data.encode()).hexdigest()
    
    def mine(self, miner_wallet:Wallet, previous_hash:str, comment:str, difficulty:int = 6) -> None:
        self.previous_hash = previous_hash
        data1 = (f"{self.transaction_id}{self.signature.signature}{self.previous_hash}{self.source.address}{self.dest.address}"
                 f"{self.amount}{self.currency.currency_id}{self.fee_amount}{self.comment}")
        data2 = f"{miner_wallet.address}"
        nonce = 0
        while True:
            data = f"{data1}{nonce}{data2}"
            hash_result = hashlib.sha256(data.encode()).hexdigest()
            if hash_result.startswith('0' * difficulty):
                break
            nonce += 1
        self.nonce = nonce
        self.miner = miner_wallet.Address
        self.miner_comment = comment
        self.miner_public_key = miner_wallet.Publickey
        self.miner_signature = miner_wallet.sign(hashlib.sha256(f"{self.transaction_id}{self.miner_comment}".encode()).hexdigest())
    
    def verify_transaction(self) -> bool:
        try:
            # public_key => source
            public_hash = hashlib.sha256(bytes.fromhex(self.public_key.str)).hexdigest()
            address = decimal_to_base62(int(public_hash, 16))
            if address != self.source.address:
                return False

            # miner_public_key => source
            public_hash = hashlib.sha256(bytes.fromhex(self.miner_public_key.str)).hexdigest()
            address = decimal_to_base62(int(public_hash, 16))
            if address != self.miner.address:
                return False

            #  signature => transaction_id
            if self.transaction_id != self.signature.str[-32:]:
                return False

            # public_key => signature
            data = f"{self.transaction_id}{self.source.address}{self.dest.address}{self.amount}{self.currency.currency_id}{self.fee_amount}{self.comment}"
            hex_data = hashlib.sha256(data.encode()).hexdigest()
            verify_source = self.public_key.verify_sign(hex_data, self.signature)

            # miner_public_key => miner_signature
            data = f"{self.transaction_id}{self.miner_comment}"
            hex_data = hashlib.sha256(data.encode()).hexdigest()
            verify_miner = self.miner_public_key.verify_sign(hex_data, self.miner_signature)

            if verify_source and verify_miner:
                return True
            return False
        except:
            return False


def amount_format(amount:int) -> str:
    amount = str(amount)
    if amount.find(',') >= 0:
        amount = int(str(amount).replace(',',''))*1000000
    
    amount = Decimal(amount)/1000000
    integer_part_with_commas = "{:,.0f}".format(amount)

    decimal_part = str(amount).split(".")[1] if '.' in str(amount) else ""
    
    if decimal_part:
        return f"{integer_part_with_commas}.{decimal_part}"
    else:
        return integer_part_with_commas

def decimal_to_base62(decimal:int):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if decimal == 0:
        return alphabet[0]
    base62 = ""
    while decimal:
        decimal, remainder = divmod(decimal, 62)
        base62 = alphabet[remainder] + base62
    return base62
