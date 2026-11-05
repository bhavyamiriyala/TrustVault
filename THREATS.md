# TrustVault – Security Threat Model

## 1. Introduction

TrustVault is a secure document-sharing web application developed using Python and Django.

It allows registered users to upload, manage and share documents with other users. Documents can be shared with Read or Edit permissions.

The main security objective is to ensure that only authorized users can access or modify documents and that important activities are recorded in an audit trail.

This document identifies potential threats, their impact, and the security measures required to prevent them.

---

## 2. Assets to Protect

The following assets must be protected:

1. User account information and passwords.
2. Uploaded documents and their contents.
3. Document ownership information.
4. Read and Edit permissions.
5. Email OTP verification codes.
6. Audit trail records.
7. Application configuration and secret keys.
8. User session information.

---

## 3. Threat Identification and Mitigation

### Threat 1: Unauthorized Document Access

**Description:**

An attacker may try to access another user's private document by changing the document ID or directly entering a document URL.

**Impact:**

Confidential documents may be viewed or downloaded without the owner's permission.

**Mitigation:**

- Verify document ownership on the server.
- Check sharing permissions before providing document access.
- Allow access only to the owner or authorized shared users.
- Return an appropriate error when access is denied.
- Never depend only on frontend restrictions.

**Security Test:**

Log in using an unauthorized account and attempt to access another user's document using its URL or document ID.

### Threat 2: Privilege Escalation

**Description:**

A user with Read permission may attempt to perform operations that require Edit permission.

**Impact:**

Unauthorized modification or deletion of document information may occur.

**Mitigation:**

- Enforce Read and Edit permissions on the server.
- Allow editing only to the document owner or an authorized Edit user.
- Verify permissions for every edit request.
- Do not trust buttons or controls hidden in the frontend as security measures.

**Security Test:**

Log in as a Read-only user and attempt to edit a shared document through a direct request.

### Threat 3: Unauthorized Permission Revocation

**Description:**

A shared user may attempt to revoke another user's access or change document-sharing permissions.

**Impact:**

Legitimate users may lose access to important documents.

**Mitigation:**

- Allow only the document owner to manage sharing permissions.
- Verify document ownership before revoking access.
- Validate the requested permission changes on the server.

**Security Test:**

Attempt to revoke a user's document access using a non-owner account.

### Threat 4: Malicious File Upload

**Description:**

An attacker may upload executable files or harmful content disguised as permitted document formats.

**Impact:**

Malicious files may affect the application or other users who download them.

**Mitigation:**

- Restrict allowed file extensions.
- Enforce maximum file size.
- Validate uploaded files on the server.
- Consider MIME type and file-content validation.
- Use malware scanning for production uploads.

**Security Test:**

Attempt to upload unsupported file types and files exceeding the allowed size.

### Threat 5: Account Impersonation

**Description:**

An attacker may attempt to access another user's account using stolen credentials or by exploiting weak authentication.

**Impact:**

The attacker may gain access to private documents and account information.

**Mitigation:**

- Use Django authentication.
- Store passwords using secure password hashing.
- Verify email addresses using OTP during registration.
- Apply appropriate login protections.
- Use secure session settings.

**Security Test:**

Attempt login using invalid credentials and verify that unauthorized login attempts are rejected.

### Threat 6: OTP Guessing and Abuse

**Description:**

An attacker may repeatedly request or guess OTP verification codes.

**Impact:**

Account verification may be abused or disrupted.

**Mitigation:**

- Set an expiry time for OTP codes.
- Limit OTP verification attempts.
- Apply rate limiting to OTP requests.
- Avoid exposing OTP values in production responses or logs.
- Invalidate OTP codes after successful verification.

**Security Test:**

Check OTP expiry, invalid OTP handling and verification attempt limits.

### Threat 7: Audit Trail Tampering

**Description:**

A user may attempt to modify, delete or access audit records without authorization.

**Impact:**

Important activity records may become unreliable, reducing accountability.

**Mitigation:**

- Restrict audit trail access to authorized users.
- Record important document activities on the server.
- Store the actor, document, action and timestamp.
- Prevent ordinary users from modifying audit records.
- Consider stronger audit log protection for production.

**Security Test:**

Attempt to access another owner's audit trail and check whether unauthorized modification is possible.

### Threat 8: Cross-Site Request Forgery (CSRF)

**Description:**

An attacker may trick an authenticated user into submitting an unwanted request to the application.

**Impact:**

Actions such as editing documents, sharing documents or revoking permissions may be performed without the user's intention.

**Mitigation:**

- Enable Django CSRF protection.
- Include CSRF tokens in forms.
- Use POST requests for sensitive operations.
- Avoid performing sensitive actions through GET requests.

**Security Test:**

Submit a sensitive POST request without a valid CSRF token and verify that it is rejected.

### Threat 9: Sensitive Information Exposure

**Description:**

Secret keys, email passwords, database credentials or other sensitive configuration values may accidentally become publicly accessible.

**Impact:**

Attackers may compromise the application or its user accounts.

**Mitigation:**

- Store secrets in environment variables.
- Exclude `.env` files from Git.
- Disable DEBUG mode in production.
- Use a secure production secret key.
- Configure allowed hosts correctly.

**Security Test:**

Inspect the repository and deployment configuration for accidentally exposed secrets.

### Threat 10: Insecure Deployment and File Storage

**Description:**

Incorrect production configuration or publicly accessible file storage may expose documents and application data.

**Impact:**

Confidential documents may be exposed, modified or lost.

**Mitigation:**

- Use HTTPS in production.
- Configure secure cookies and allowed hosts.
- Use private file storage.
- Restrict direct access to uploaded documents.
- Configure database backups.
- Apply production security settings.

**Security Test:**

Open the deployed website in a private browser window and test document access using different user accounts.

---

## 4. Security Testing Plan

The following security tests must be performed before final submission.

| Test ID | Security Test                               | Expected Result       |
| ------- | ------------------------------------------- | --------------------- |
| ST01    | Unauthorized user accesses private document | Access denied         |
| ST02    | Read user attempts to edit document         | Editing denied        |
| ST03    | Edit user edits an authorized document      | Editing allowed       |
| ST04    | Non-owner attempts to revoke access         | Access denied         |
| ST05    | Unsupported file upload                     | Upload rejected       |
| ST06    | Oversized file upload                       | Upload rejected       |
| ST07    | Invalid login attempt                       | Login rejected        |
| ST08    | Invalid or expired OTP                      | Verification rejected |
| ST09    | User accesses another owner's audit trail   | Access denied         |
| ST10    | POST request without valid CSRF token       | Request rejected      |

**Note:** These are planned security tests. Record the actual results after executing them. Do not mark a test as passed without evidence.

---

## 5. Risk Assessment

| Threat                          | Potential Impact               | Priority |
| ------------------------------- | ------------------------------ | -------- |
| Unauthorized document access    | Confidentiality loss           | Critical |
| Privilege escalation            | Unauthorized modification      | Critical |
| Permission revocation abuse     | Loss of access control         | High     |
| Malicious file upload           | Application or user compromise | High     |
| Account impersonation           | Account compromise             | High     |
| OTP abuse                       | Authentication compromise      | High     |
| Audit trail tampering           | Loss of accountability         | High     |
| CSRF                            | Unauthorized actions           | High     |
| Sensitive information exposure  | Application compromise         | Critical |
| Insecure deployment and storage | Data exposure or loss          | Critical |

---

## 6. Known Security Limitations

The following areas require additional verification or improvement before production deployment:

1. Malware scanning for uploaded documents.
2. Stronger file-content and MIME validation.
3. Rate limiting for login and OTP verification.
4. Private production file storage.
5. Production database and backup configuration.
6. Additional protection for audit records.
7. Security testing of all document authorization operations.

These items must not be considered implemented unless they have actually been configured and tested.

---

## 7. Security Principles Followed

TrustVault follows these security principles:

- **Authentication:** Verify the identity of users before allowing access.
- **Authorization:** Allow users to perform only the operations they are permitted to perform.
- **Least Privilege:** Give users only the minimum permissions required.
- **Confidentiality:** Protect private documents from unauthorized access.
- **Integrity:** Prevent unauthorized modification of documents and records.
- **Accountability:** Maintain an audit trail of important activities.
- **Defense in Depth:** Use multiple security controls instead of depending on a single protection mechanism.

---

## 8. Conclusion

TrustVault aims to provide secure document storage and sharing through authentication, ownership verification, permission-based access and audit logging.

The main security focus is preventing unauthorized document access and ensuring that every sensitive operation is verified on the server.

The identified threats and security tests will be reviewed throughout development to improve the application's security and reliability.
