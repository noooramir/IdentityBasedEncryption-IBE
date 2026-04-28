# Member 1 Presentation Script (Areeba)

## Slide 1 - Role and Scope
**Title:** Identity-Based Encryption (IBE) Core and Threat Modeling  
**On-slide bullets:**
- Project topic: Boneh-Franklin IBE
- My role: Cryptographic core + threat modeling
- Deliverables: IBE module, KGC flow, STRIDE, DFD

**Speaker notes (what to say):**  
"My portion focuses on the cryptographic foundation of the system. I implemented the Boneh-Franklin IBE flow with KGC setup, identity-based key extraction, encryption, and decryption. I also developed the threat model, including STRIDE analysis and the system DFD."

---

## Slide 2 - Why IBE for This Project
**Title:** Why Identity-Based Encryption?  
**On-slide bullets:**
- Public key = user identity (e.g., email)
- No certificate lookup needed for senders
- Suitable for controlled organizational communication
- Trade-off: stronger trust in KGC

**Speaker notes:**  
"In this model, the sender can encrypt using the recipient’s identity directly, such as an email address. This simplifies key discovery compared to traditional PKI. The major trade-off is trust concentration in the KGC, which must be strongly protected."

---

## Slide 3 - Cryptographic Workflow
**Title:** Boneh-Franklin IBE Flow  
**On-slide bullets:**
- Setup: KGC generates MPK and MSK
- Extract: KGC derives private key SK_ID for each identity
- Encrypt: sender encrypts using recipient identity + MPK
- Decrypt: recipient uses SK_ID to recover plaintext

**Speaker notes:**  
"First, KGC runs setup and creates public parameters and a master secret. Then, for each verified user identity, it issues a private key. Senders encrypt using only identity and public parameters. The recipient decrypts using their identity private key."

---

## Slide 4 - Hybrid Encryption in Implementation
**Title:** Practical Implementation Detail  
**On-slide bullets:**
- Random session element chosen in pairing group
- Session element encrypted via IBE
- Symmetric key derived from session element
- Plaintext encrypted using symmetric cipher

**Speaker notes:**  
"To handle normal message data efficiently, I used a hybrid design. IBE protects a random session element, and that element derives a symmetric key for encrypting the actual message. This is practical and aligns with real cryptographic system design patterns."

---

## Slide 5 - Threat Model Summary
**Title:** Threat Model and Trust Boundaries  
**On-slide bullets:**
- Assets: MSK, SK_ID, messages, identity metadata
- Adversaries: network attacker, insider misuse, impersonation
- Trust boundaries: client-backend, backend-KGC, services-database
- Security goals: confidentiality, integrity, availability, accountability

**Speaker notes:**  
"I modeled key assets and attacker capabilities, then mapped trust boundaries across the architecture. The most sensitive asset is the KGC master secret key, because compromise of MSK can affect all identities."

---

## Slide 6 - STRIDE Findings and Mitigations
**Title:** STRIDE Analysis Highlights  
**On-slide bullets:**
- Spoofing: fake key extraction requests -> MFA + strict identity verification
- Tampering: ciphertext changes in transit -> integrity checks + authenticated encryption
- Information disclosure: MSK leakage -> HSM/KMS + strict secret controls
- DoS/EoP: endpoint abuse -> rate limiting + least-privilege IAM

**Speaker notes:**  
"The STRIDE analysis helped map concrete threats to practical controls. The highest impact scenario is information disclosure of MSK. So hardening KGC secret storage and controlling privileged access are top priorities."

---

## Slide 7 - Key Takeaway and Handoff
**Title:** Outcome of Member 1 Work  
**On-slide bullets:**
- Working IBE core prototype completed
- KGC setup and key extraction flow defined
- Threat model + STRIDE + DFD prepared for final report
- Clear API handoff provided to backend teammate

**Speaker notes:**  
"My deliverables provide both the cryptographic engine and the security design baseline. This supports integration with backend and frontend modules while keeping security assumptions explicit for evaluation and demo."

---

## Quick Q&A Prep (for class)
- **Q:** Why not use normal PKI certificates?  
  **A:** IBE simplifies public-key discovery by using identity as public key; better fit for controlled environments.

- **Q:** What is the biggest risk in IBE?  
  **A:** KGC master secret compromise; mitigated with hardened key management and strict operational controls.

- **Q:** Is this production-ready?  
  **A:** It is a functional academic prototype; production needs stronger deployment hardening, auditing, and key lifecycle controls.
