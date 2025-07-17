import hashlib
import json
import os
import time
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

BLOCKCHAIN_FILE = 'blockchain.json'

class Block:
    def __init__(self, index, previous_hash, file_hash, user_id, timestamp, block_hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.file_hash = file_hash
        self.user_id = user_id
        self.timestamp = timestamp
        self.hash = block_hash or self.calculate_hash()

    def calculate_hash(self):
        block_string = f'{self.index}{self.previous_hash}{self.file_hash}{self.user_id}{self.timestamp}'
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'file_hash': self.file_hash,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'hash': self.hash
        }

    @staticmethod
    def from_dict(data):
        return Block(
            data['index'],
            data['previous_hash'],
            data['file_hash'],
            data['user_id'],
            data['timestamp'],
            data['hash']
        )

class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()

    def create_genesis_block(self):
        genesis_block = Block(0, '0', '0', 'system', time.time())
        self.chain.append(genesis_block)
        self.save_chain()

    def add_block(self, file_path, user_id):
        file_hash = self.hash_file(file_path)
        previous_block = self.chain[-1]
        new_block = Block(
            index=previous_block.index + 1,
            previous_hash=previous_block.hash,
            file_hash=file_hash,
            user_id=user_id,
            timestamp=time.time()
        )
        self.chain.append(new_block)
        self.save_chain()
        return new_block

    def hash_file(self, file_path):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def save_chain(self):
        with open(BLOCKCHAIN_FILE, 'w') as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=2)

    def load_chain(self):
        if os.path.exists(BLOCKCHAIN_FILE):
            try:
                with open(BLOCKCHAIN_FILE, 'r') as f:
                    data = json.load(f)
                    if data and isinstance(data, list) and len(data) > 0:
                        self.chain = [Block.from_dict(block) for block in data]
                    else:
                        print('Blockchain file is empty, creating genesis block.')
                        self.create_genesis_block()
            except Exception as e:
                print(f'Error loading blockchain: {e}. Creating genesis block.')
                self.create_genesis_block()
        else:
            self.create_genesis_block()

    def to_list(self):
        return [block.to_dict() for block in self.chain]

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            # Check previous hash
            if current.previous_hash != previous.hash:
                return False
            # Check current hash
            if current.hash != current.calculate_hash():
                return False
        return True

    def verify_signature(self, block, signature_b64, public_key_pem):
        block_string = f'{block.index}{block.previous_hash}{block.file_hash}{block.user_id}{block.timestamp}'
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        
        signature = base64.b64decode(signature_b64)
        try:
            public_key.verify(
                signature,
                block_string.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def save_signature(self, block_index, signer_id, signature, public_key_pem):
        SIGNATURES_FILE = 'signatures.json'
        with open('log.json', 'w') as f:
            json.dump("test", f, indent=2)


        signature_entry = {
            'block_index': block_index,
            'signer_id': signer_id,
            'signature': signature,
            'public_key': public_key_pem,
            'signed_at': time.time()
        }
        if not os.path.exists(SIGNATURES_FILE):
            with open(SIGNATURES_FILE, 'w') as f:
                json.dump([signature_entry], f, indent=2)
        else:
            with open(SIGNATURES_FILE, 'r+') as f:
                signatures = json.load(f)
                signatures.append(signature_entry)
                f.seek(0)
                json.dump(signatures, f, indent=2)
                f.truncate() 

    def check_file_signature(self, block_index):
        SIGNATURES_FILE = 'signatures.json'
        # تحقق من وجود ملف التواقيع
        if not os.path.exists(SIGNATURES_FILE):
            return {
                'signed': False,
                'valid': False,
                'signer_id': None
            }
        # اقرأ جميع التواقيع
        with open(SIGNATURES_FILE, 'r') as f:
            signatures = json.load(f)
        # ابحث عن توقيع للبلوك المطلوب
        for entry in signatures:
            if entry['block_index'] == block_index:
                # تحقق من صحة التوقيع
                block = self.chain[block_index]
                is_valid = self.verify_signature(
                    block,
                    entry['signature'],
                    entry['public_key']
                )
                return {
                    'signed': True,
                    'valid': is_valid,
                    'signer_id': entry['signer_id']
                }
        # إذا لم يوجد توقيع
        return {
            'signed': False,
            'valid': False,
            'signer_id': None
        } 