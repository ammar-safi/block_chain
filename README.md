# Flask Blockchain API

A simple Flask-based REST API for interacting with a file-based blockchain. This project allows you to add new blocks (representing files and users), view the blockchain, and validate its integrity.

## Features

- Add a new block to the blockchain by uploading a file path and user ID
- View the entire blockchain
- Validate the integrity of the blockchain

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Flask app:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000/`.

## API Response Format

All API responses follow a standardized format:

```json
{
  "data": {},
  "status": "success|error",
  "message": "Description of the response",
  "status_code": 200
}
```

## API Endpoints

### 1. Add Block

- **POST** `/add_block`
- **Body (JSON):**
  ```json
  {
    "file_path": "path/to/your/file.txt",
    "user_id": "user123"
  }
  ```
- **Success Response:**
  ```json
  {
    "data": {
      "block": {...},
      "chain_valid": true
    },
    "status": "success",
    "message": "Block added successfully",
    "status_code": 201
  }
  ```
- **Error Response:**
  ```json
  {
    "data": null,
    "status": "error",
    "message": "file_path and user_id are required",
    "status_code": 400
  }
  ```

### 2. Get Blockchain

- **GET** `/chain`
- **Response:**
  ```json
  {
    "data": {"chain": [...]},
    "status": "success",
    "message": "Blockchain retrieved successfully",
    "status_code": 200
  }
  ```

### 3. Validate Blockchain

- **GET** `/validate_chain`
- **Response:**
  ```json
  {
    "data": { "chain_valid": true },
    "status": "success",
    "message": "Blockchain validation completed",
    "status_code": 200
  }
  ```

### 4. Fetch Block Data for Signing

- **GET** `/block/<index>`
- **Response:**
  ```json
  {
    "data": {"block": {...}},
    "status": "success",
    "message": "Block retrieved successfully",
    "status_code": 200
  }
  ```

### 5. Submit Signature to Flask

- **POST** `/sign_block`
- **Body (JSON):**
  ```json
  {
    "block_index": 2,
    "signer_id": "user123",
    "signature": "BASE64_SIGNATURE",
    "public_key": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
  }
  ```
- **Success Response:**
  ```json
  {
    "data": { "signature_saved": true },
    "status": "success",
    "message": "Signature saved successfully",
    "status_code": 201
  }
  ```

### 6. Check Block Signature

- **GET** `/check_signature/<index>`
- **Response:**
  - If the block is not signed :
    ```json
    {
      "data": {
        "signed": false,
        "valid": false,
        "signer_id": null
      },
      "status": "success",
      "message": "Signature check completed",
      "status_code": 200
    }
    ```
  - If the block is signed:
    ```json
    {
      "data": {
        "signed": true,
        "valid": true,
        "signer_id": "user123"
      },
      "status": "success",
      "message": "Signature check completed",
      "status_code": 200
    }
    ```
    - If the block does not exist :
    ```json
    {
      "data": null,
      "message": "Block not found",
      "status": "error",
      "status_code": 400
    }
    ```

## Signature Verification Feature

- The API now supports verifying if a block (file) is signed and whether the signature is valid.
- The endpoint `/check_signature/<index>` returns whether the block is signed, if the signature is valid, and the signer ID if available.
- This is useful for confirming the authenticity and integrity of files on the blockchain.

## Blockchain Structure

Each block contains:

- `
