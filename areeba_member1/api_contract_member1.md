# file name : api_contract_member1.md
# Member 1 -> Member 2 API Contract (IBE + KGC)

## Public Parameters Endpoint
- **Route:** `GET /kgc/public-params`
- **Purpose:** Returns serialized master public parameters (MPK).

## Key Extraction Endpoint
- **Route:** `POST /kgc/extract-key`
- **Input JSON:**
```json
{
  "identity": "user@example.com"
}
```
- **Output JSON:** Serialized identity private key `SK_ID`.

## Encrypt Endpoint
- **Route:** `POST /crypto/encrypt`
- **Input JSON:**
```json
{
  "recipient_identity": "user@example.com",
  "message": "hello"
}
```
- **Output JSON:** Ciphertext payload serialized for transport.

## Decrypt Endpoint
- **Route:** `POST /crypto/decrypt`
- **Input JSON:**
```json
{
  "identity": "user@example.com",
  "ciphertext": {}
}
```
- **Output JSON:** Plaintext or success/failure marker.

## Notes
- Backend owner should handle serialization/deserialization for pairing objects.
- Identity canonicalization should be consistent (trim + lowercase recommended).
- KGC private material (MSK) must never leave server.
