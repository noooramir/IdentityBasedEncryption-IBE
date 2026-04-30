# file name : dfd_tmt_blueprint_only.md

# DFD/TMT Blueprint Only (Member 1)

Use this file to build the diagram in Microsoft Threat Modeling Tool.

## 1) Components to Add
- External Interactor: `Sender Client`
- External Interactor: `Recipient Client`
- Process: `API Backend Service`
- Process: `KGC Service`
- Data Store: `Identity & Metadata DB`
- Data Store: `Audit Log Store`

## 2) Data Flows to Draw
1. `Sender Client -> API Backend Service`  
   `Encrypt Request (recipient_id, plaintext)`
2. `API Backend Service -> KGC Service`  
   `Public Params / Crypto Request`
3. `KGC Service -> API Backend Service`  
   `MPK / Crypto Response`
4. `API Backend Service -> Sender Client`  
   `Encrypted Bundle (ID, C_ibe, C_msg)`
5. `Recipient Client -> API Backend Service`  
   `Key Extraction Request (identity, auth proof)`
6. `API Backend Service -> KGC Service`  
   `Key Issuance Request`
7. `KGC Service -> API Backend Service`  
   `Issued Private Key Material`
8. `API Backend Service -> Recipient Client`  
   `Protected SK_ID Delivery`
9. `Recipient Client -> API Backend Service`  
   `Decrypt Request (optional if server-side decrypt flow)`
10. `API Backend Service <-> Identity & Metadata DB`  
    `Identity + Issuance Metadata`
11. `API Backend Service -> Audit Log Store`  
    `Security Audit Events`

## 3) Trust Boundaries
- Around clients: `Untrusted Client Zone`
- Around backend + kgc: `Internal Service Zone`
- Around kgc only: `High Trust KGC Zone`
- Around stores: `Protected Data Zone`

## 4) STRIDE Threats to Attach
- **Spoofing:** fake identity requests key extraction
- **Tampering:** ciphertext/identity modified in transit
- **Repudiation:** denial of issuance/admin actions
- **Information Disclosure:** MSK leak or SK_ID exposure
- **Denial of Service:** endpoint flooding
- **Elevation of Privilege:** unauthorized service reaches KGC secrets

## 5) Suggested Mitigations
- MFA + strict identity verification before key issuance
- TLS + authenticated encryption + metadata integrity checks
- Immutable audit logs with timestamps and request IDs
- HSM/KMS for MSK, encrypted SK_ID delivery, least privilege IAM
- Rate limiting, throttling, monitoring and alerting
- Network segmentation for KGC and secret stores
