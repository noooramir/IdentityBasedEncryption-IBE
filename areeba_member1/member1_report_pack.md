# Member 1 Report Pack (Areeba)

## 1) Cryptographic Core: Boneh-Franklin Identity-Based Encryption

### 1.1 Objective
The cryptographic core implements the Boneh-Franklin Identity-Based Encryption (IBE) scheme to allow encryption using a user's identity string (e.g., email) as the public key. This removes the need for conventional public-key certificate distribution and supports the project goal of a secure organizational messaging workflow.

### 1.2 Design Rationale
Traditional PKI requires certificate issuance, validation, and revocation infrastructure. In IBE, the user's identity is mapped to a public key and the Key Generation Center (KGC) issues the corresponding private key. This simplifies key discovery in controlled organizational contexts where KGC trust is acceptable.

### 1.3 Cryptographic Components
- **Pairing group:** Bilinear pairing group instantiated via Charm-Crypto (`SS512`).
- **IBE scheme:** `IBE_BonehFranklin` implementation from Charm.
- **KGC master keys:** `MPK` (public parameters) and `MSK` (master secret key).
- **Hybrid encryption layer:** A random session element in `GT` is IBE-encrypted; a symmetric key derived from that element encrypts application plaintext.

### 1.4 Core Algorithms and Flow
1. **Setup (KGC)**
   - Input: security parameter / pairing curve.
   - Operation: initialize pairing group and run IBE setup.
   - Output: `MPK`, `MSK`.

2. **Extract (KGC for identity ID)**
   - Input: `MSK`, identity string `ID`.
   - Operation: derive identity private key `SK_ID`.
   - Output: `SK_ID`.

3. **Encrypt (Sender for recipient ID)**
   - Input: `MPK`, recipient identity `ID`, plaintext `M`.
   - Operation:
     - choose random session element `R in GT`
     - compute IBE ciphertext `C_ibe = Enc(MPK, ID, R)`
     - derive symmetric key `K = H(R)`
     - compute message ciphertext `C_msg = SymEnc(K, M)`
   - Output: ciphertext bundle `{ID, C_ibe, C_msg}`.

4. **Decrypt (Recipient with SK_ID)**
   - Input: `MPK`, `SK_ID`, bundle `{ID, C_ibe, C_msg}`.
   - Operation:
     - recover `R' = Dec(MPK, SK_ID, C_ibe)`
     - derive `K' = H(R')`
     - recover `M' = SymDec(K', C_msg)`
   - Output: plaintext `M'` and validity status.

### 1.5 Security Assumptions and Limitations
- Security relies on bilinear pairing hardness assumptions (as modeled by Boneh-Franklin).
- KGC is highly trusted; compromise of `MSK` compromises all identities.
- Secure channels are required for private key delivery (`SK_ID`) from KGC to users.
- This project prototype prioritizes clarity and integration; production deployment requires hardened key storage, HSM/KMS, auditing, and lifecycle controls.

### 1.6 Implementation Scope (Member 1)
- Implemented KGC setup, extract, encrypt, and decrypt functions in `areeba_member1/ibe_core.py`.
- Implemented a hybrid flow so real plaintext is encrypted and recovered.
- Produced API contract for backend integration in `areeba_member1/api_contract_member1.md`.

---

## 2) Threat Model

### 2.1 System Assets
- Master Secret Key (`MSK`) at KGC.
- Identity private keys (`SK_ID`) issued to users.
- Master public parameters (`MPK`).
- Message plaintext and ciphertext payloads.
- Identity registry and issuance logs.
- Backend service credentials and configuration.

### 2.2 Security Objectives
- **Confidentiality:** only intended identity owner can decrypt messages.
- **Integrity:** message payloads and cryptographic metadata cannot be silently altered.
- **Authenticity:** user identity and KGC operations are verifiable.
- **Availability:** KGC and crypto services remain operational under normal attack pressure.
- **Accountability:** sensitive actions are logged for audit and incident response.

### 2.3 Adversary Model
- Network attacker capable of interception, replay, and modification (MitM conditions).
- Malicious insider attempting unauthorized key extraction.
- Compromised client endpoint attempting impersonation.
- Opportunistic attacker abusing weak input validation and API controls.

### 2.4 Trust Boundaries
- Boundary A: Client device <-> Backend API (untrusted network).
- Boundary B: Backend service <-> KGC module (privileged internal boundary).
- Boundary C: Backend/KGC <-> Database (data-at-rest and service credential boundary).
- Boundary D: Administrator/operator access <-> production services.

### 2.5 Key Assumptions
- TLS is enabled for all client-server traffic.
- KGC host is more strongly protected than standard application nodes.
- Identities are unique and verified before key issuance.
- Issued private keys are stored securely by clients.

---

## 3) STRIDE Threat Enumeration

| STRIDE Category | Example Threat in IBE System | Impact | Mitigation |
|---|---|---|---|
| **S - Spoofing** | Attacker requests key extraction for another user's identity | Unauthorized decryption capability | Strong user authentication (MFA), identity verification workflow, signed issuance tokens |
| **T - Tampering** | Ciphertext or identity field modified in transit | Decryption failure or malicious content substitution | Authenticated encryption for payload, request signing, integrity checks on metadata |
| **R - Repudiation** | User or admin denies requesting key issuance | Weak forensic traceability | Immutable audit logs, request IDs, timestamped signed logs |
| **I - Information Disclosure** | MSK leak or insecure SK_ID transport | Global confidentiality collapse (MSK) / per-user compromise (SK_ID) | HSM/KMS for MSK, encrypted key delivery, strict secret handling and rotation policies |
| **D - Denial of Service** | Flooding key extraction/encrypt endpoints | Service outage, delayed operations | Rate limits, API gateway throttling, autoscaling, circuit breakers |
| **E - Elevation of Privilege** | Low-privilege service account accesses KGC secrets | Full system compromise escalation | Least privilege IAM, network segmentation, secret-scoped service accounts, periodic permission audits |

---

## 4) Data Flow Diagram (DFD) Blueprint for Microsoft TMT

### 4.1 Entities and Processes to Create
- **External Interactor:** Sender Client
- **External Interactor:** Recipient Client
- **Process:** API Backend Service
- **Process:** KGC Service
- **Data Store:** Identity & Metadata DB
- **Data Store:** Audit Log Store

### 4.2 Data Flows to Draw
1. Sender Client -> API Backend: encrypt request `{recipient_id, plaintext}`
2. API Backend -> KGC Service: fetch/validate public parameters
3. KGC Service -> API Backend: `MPK`/crypto response
4. API Backend -> Sender Client: encrypted bundle `{ID, C_ibe, C_msg}`
5. Recipient Client -> API Backend: key extraction request `{identity, auth proof}`
6. API Backend -> KGC Service: key issuance request
7. KGC Service -> API Backend: identity private key material (protected channel)
8. API Backend -> Recipient Client: issued private key (protected delivery)
9. Recipient Client -> API Backend: decrypt request (or local decrypt if client-side)
10. API Backend <-> Identity & Metadata DB: user identity and issuance metadata
11. API Backend -> Audit Log Store: issuance/encryption/decryption security logs

### 4.3 Trust Boundaries to Mark in TMT
- Between clients and backend (internet/untrusted zone).
- Between backend and KGC (restricted internal zone).
- Around KGC + secrets handling component (high-trust zone).
- Between services and data stores (data protection boundary).

### 4.4 Threats to Attach in TMT
- Spoofing on key extraction flow.
- Tampering on ciphertext transport flow.
- Information disclosure on MSK/SK_ID handling.
- DoS on API ingress and KGC issuance endpoint.
- Elevation of privilege on backend-to-KGC service identity.

---

## 5) Suggested Validation Experiments (Member 1)

1. **Correctness Test:** same identity decrypts successfully.
2. **Wrong-Key Test:** different identity key fails to recover valid message.
3. **Tamper Test:** modify ciphertext field and verify decryption/integrity failure.
4. **Replay Observation:** replay old extraction/decrypt requests and validate logging + replay controls (if implemented by backend).
5. **Performance Snapshot:** average setup/extract/encrypt/decrypt latency over N iterations.

---

## 6) Short Conclusion (Report-Ready)

The implemented Boneh-Franklin IBE core demonstrates identity-driven encryption with a centralized KGC model suitable for controlled organizational messaging environments. The design reduces public-key distribution complexity while introducing critical trust concentration at the KGC, making strong key protection, audited key issuance, and secure operational controls essential to system security.
