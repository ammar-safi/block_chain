from flask import Flask, jsonify, request
from blockchain import Blockchain
from response_handler import ResponseHandler
import os

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/add_block', methods=['POST'])
def add_block():
    data = request.get_json()
    file_path = data.get('file_path')
    user_id = data.get('user_id')
    if not file_path or not user_id:
        return ResponseHandler.validation_error(
            message='file_path and user_id are required'
        )
    if not os.path.exists(file_path):
        return ResponseHandler.validation_error(
            message='File does not exist'
        )
    try:
        new_block = blockchain.add_block(file_path, user_id)
        is_valid = blockchain.is_valid()
        return ResponseHandler.success(
            data={
                'block': new_block.to_dict(),
                'chain_valid': is_valid
            },
            message='Block added successfully',
            status_code=201
        )
    except Exception as e:
        return ResponseHandler.server_error(
            message=str(e)
        )

@app.route('/chain', methods=['GET'])
def get_chain():
    return ResponseHandler.success(
        data={'chain': blockchain.to_list()},
        message='Blockchain retrieved successfully'
    )

@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    is_valid = blockchain.is_valid()
    if not is_valid:
        return ResponseHandler.error(
            message='Blockchain is not valid',

        )
    return ResponseHandler.success(
        data={'chain_valid': is_valid},
        message='Blockchain validation completed'
    )

@app.route('/block/<int:index>', methods=['GET'])
def get_block(index):
    if index < 0 or index >= len(blockchain.chain):
        return ResponseHandler.not_found(
            message='Block not found'
        )
    block = blockchain.chain[index]
    return ResponseHandler.success(
        data={'block': block.to_dict()},
        message='Block retrieved successfully'
    )

@app.route('/sign_block', methods=['POST'])
def sign_block():
    data = request.get_json()
    block_index = data.get('block_index')
    signer_id = data.get('signer_id')
    signature = data.get('signature')
    public_key = data.get('public_key')
    
    if block_index is None or not signer_id or not signature or not public_key:
        return ResponseHandler.validation_error(
            message='block_index, signer_id, signature, and public_key are required'
        )
    if block_index < 0 or block_index >= len(blockchain.chain):
        return ResponseHandler.not_found(
            message='Block not found'
        )
    block = blockchain.chain[block_index]
    if not blockchain.verify_signature(block, signature, public_key):
        return ResponseHandler.validation_error(
            message='Invalid signature'
        )
    try:
        blockchain.save_signature(block_index, signer_id, signature, public_key)
        return ResponseHandler.success(
            data={'signature_saved': True},
            message='Signature saved successfully',
            status_code=201
        )
    except Exception as e:
        return ResponseHandler.server_error(
            message=str(e)
        )

@app.route('/check_signature/<int:index>', methods=['GET'])
def check_signature(index):
    if index < 0 or index >= len(blockchain.chain):
        return ResponseHandler.error(
            message='Block not found'
        )
    result = blockchain.check_file_signature(index)
    return ResponseHandler.success(
        data=result,
        message='Signature check completed'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 