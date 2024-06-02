import os
import json
import base64
from hashlib import sha256
import hashlib
from time import time
from flask import Flask, jsonify, request
import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

sys.path.append("../")
from blockchain.smart_contracts import *

app = Flask(__name__)

# 智能合约实例化
identity_management = IdentityManagementContract()
data_encryption = DataEncryptionContract()
clinical_trial = ClinicalTrialContract()
drug_regulation = DrugRegulationContract()
intellectual_property = IntellectualPropertyContract()

# RSA 密钥对生成
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()

# 身份管理合约端点
@app.route('/roles/add', methods=['POST'])
def add_role():
    values = request.get_json()
    user = values.get('user')
    role = values.get('role')
    if not user or not role:
        return jsonify({'error': 'Missing user or role'}), 400
    identity_management.add_role(user, role)
    blockchain.add_transaction("system", user, {"action": "add_role", "role": role})
    return jsonify({'message': f'Role {role} assigned to user {user}'}), 201

@app.route('/roles/check', methods=['GET'])
def check_role():
    user = request.args.get('user')
    role = request.args.get('role')
    if not user or not role:
        return jsonify({'error': 'Missing user or role'}), 400
    result = identity_management.check_role(user, role)
    # 记录检查操作到区块链
    action_details = {"action": "check_role", "user": user, "role": role, "result": "matches" if result else "does not match"}
    blockchain.add_transaction("system", "identity_management", action_details)
    if result:
        return jsonify({'result': 'Role matches'}), 200
    else:
        return jsonify({'result': 'Role does not match'}), 404
    
@app.route('/encrypt', methods=['POST'])
def encrypt_data():
    values = request.get_json()
    user = values.get('user')
    data = values.get('data')
    if not user or not data:
        return jsonify({'error': 'Missing user or data'}), 400
    if not os.path.exists(f'info/{user}.json'):
        return jsonify({'error': 'User not found'}), 404

    with open(f'info/{user}.json', 'r') as f:
        user_info = json.load(f)
    
    public_key_pem = user_info['public_key']
    public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))

    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_data_b64 = base64.b64encode(encrypted_data).decode('utf-8')

    blockchain.add_transaction("system", "data_encryption", {"action": "encrypt_data", "user": user, "data": data})
    return jsonify({'encrypted_data': encrypted_data_b64}), 201

@app.route('/decrypt', methods=['POST'])
def decrypt_data():
    values = request.get_json()
    user = values.get('user')
    encrypted_data_b64 = values.get('encrypted_data')
    if not user or not encrypted_data_b64:
        return jsonify({'error': 'Missing user or encrypted data'}), 400
    if not os.path.exists(f'info/{user}.json'):
        return jsonify({'error': 'User not found'}), 404

    with open(f'info/{user}_private.pem', 'r') as f:
        private_key_pem = f.read()
    
    private_key = serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
    encrypted_data = base64.b64decode(encrypted_data_b64)

    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    blockchain.add_transaction("system", "data_encryption", {"action": "decrypt_data", "user": user, "encrypted_data": encrypted_data_b64})
    return jsonify({'decrypted_data': decrypted_data.decode('utf-8')}), 201

@app.route('/trial/add', methods=['POST'])
def add_trial():
    values = request.get_json()
    trial_id = values.get('trial_id')
    trial_data = values.get('trial_data')
    if not trial_id or not trial_data:
        return jsonify({'error': 'Missing trial_id or trial_data'}), 400
    clinical_trial.add_trial(trial_id, trial_data)
    blockchain.add_transaction("system", "clinical_trial", {"action": "add_trial", "trial_id": trial_id, "trial_data": trial_data})
    return jsonify({'message': f'Trial {trial_id} added'}), 201

@app.route('/trial/get', methods=['GET'])
def get_trial():
    trial_id = request.args.get('trial_id')
    if not trial_id:
        return jsonify({'error': 'Missing trial_id'}), 400
    trial_data = clinical_trial.get_trial(trial_id)
    if trial_data:
        return jsonify({'trial_data': trial_data}), 200
    else:
        return jsonify({'error': 'Trial not found'}), 404


@app.route('/regulation/add', methods=['POST'])
def add_regulation():
    values = request.get_json()
    drug_id = values.get('drug_id')
    regulation_data = values.get('regulation_data')
    if not drug_id or not regulation_data:
        return jsonify({'error': 'Missing drug_id or regulation_data'}), 400
    drug_regulation.add_regulation(drug_id, regulation_data)
    blockchain.add_transaction("system", "drug_regulation", {"action": "add_regulation", "drug_id": drug_id, "regulation_data": regulation_data})
    return jsonify({'message': f'Regulation for drug {drug_id} added'}), 201

@app.route('/regulation/check', methods=['GET'])
def check_compliance():
    drug_id = request.args.get('drug_id')
    if not drug_id:
        return jsonify({'error': 'Missing drug_id'}), 400
    if drug_regulation.check_compliance(drug_id):
        return jsonify({'result': 'Drug is compliant'}), 200
    else:
        return jsonify({'result': 'Drug is not compliant'}), 404


@app.route('/ip/register', methods=['POST'])
def register_ip():
    values = request.get_json()
    ip_id = values.get('ip_id')
    ip_data = values.get('ip_data')
    if not ip_id or not ip_data:
        return jsonify({'error': 'Missing ip_id or ip_data'}), 400
    intellectual_property.register_ip(ip_id, ip_data)
    # 将操作记录为交易
    blockchain.add_transaction("system", "intellectual_property", {"action": "register_ip", "ip_id": ip_id, "ip_data": ip_data})
    return jsonify({'message': f'IP {ip_id} registered successfully'}), 201

@app.route('/ip/transfer', methods=['POST'])
def transfer_ip():
    values = request.get_json()
    ip_id = values.get('ip_id')
    new_owner = values.get('new_owner')
    if not ip_id or not new_owner:
        return jsonify({'error': 'Missing ip_id or new_owner'}), 400
    if ip_id in intellectual_property.ip_records:
        intellectual_property.transfer_ip(ip_id, new_owner)
        # 将操作记录为交易
        blockchain.add_transaction("system", "intellectual_property", {"action": "transfer_ip", "ip_id": ip_id, "new_owner": new_owner})
        return jsonify({'message': f'IP {ip_id} transferred to {new_owner}'}), 200
    else:
        return jsonify({'error': 'IP not found'}), 404


class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.new_block(previous_hash='1', proof=100)
        self.load_chain()

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1] if self.chain else {'proof': 100}),
        }
        self.pending_transactions = []
        self.chain.append(block)
        self.save_block(block)
        return block

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, data):
        self.pending_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'data': data
        })

    def save_block(self, block):
        index = block['index']
        if not os.path.exists('blocks'):
            os.makedirs('blocks')
        with open(f'blocks/block_{index}.json', 'w') as f:
            json.dump(block, f)

    def load_chain(self):
        if not os.path.exists('blocks'):
            os.makedirs('blocks')
        files = sorted(os.listdir('blocks'), key=lambda x: int(x.split('_')[1].split('.')[0]))
        for filename in files:
            path = os.path.join('blocks', filename)
            with open(path, 'r') as f:
                block = json.load(f)
                self.chain.append(block)

@app.route('/register', methods=['POST'])
def register_user():
    values = request.get_json()
    user = values.get('user')
    if not user:
        return jsonify({'error': 'Missing user'}), 400
    if os.path.exists(f'info/{user}.json'):
        return jsonify({'error': 'User already exists'}), 400

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # 存储私钥和公钥
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    user_info = {
        'username': user,
        'public_key': public_key_pem
    }

    if not os.path.exists('info'):
        os.makedirs('info')

    with open(f'info/{user}.json', 'w') as f:
        json.dump(user_info, f)

    with open(f'info/{user}_private.pem', 'w') as f:
        f.write(private_key_pem)

    return jsonify({'public_key': public_key_pem}), 201

@app.route('/get_public_key', methods=['GET'])
def get_public_key():
    user = request.args.get('user')
    if not user:
        return jsonify({'error': 'Missing user'}), 400
    if not os.path.exists(f'info/{user}.json'):
        return jsonify({'error': 'User not found'}), 404

    with open(f'info/{user}.json', 'r') as f:
        user_info = json.load(f)

    public_key_pem = user_info['public_key']

    return jsonify({'public_key': public_key_pem}), 200

# 实例化区块链
blockchain = Blockchain()

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
        # 这里应该添加交易到挂起的交易列表，本示例中省略

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block()
    proof = last_block['proof'] + 1  # 简化的工作证明
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    return jsonify(block), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
    'chain': blockchain.chain,
    'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)