# TrustVault – Security Threat Model

## 1. Introduction

TrustVault is a secure document-sharing web application developed using Python and Django.

It allows registered users to upload, manage and share documents with other users. Documents can be shared with Read or Edit permissions.

The main security objective is to ensure that only authorized users can access or modify documents and that important activities are recorded in an audit trail.

This document identifies potential threats, their impact, implemented security measures and areas requiring further improvement.

---

## 2. Assets to Protect

The following assets must be protected:

1. User account information and passwords.
2. Uploaded documents and their contents.
3. Document ownership information.
4. Read and Edit permissions.
5. Audit trail records.
6. Application configuration and secret keys.
7. User session information.
8. Administrator accounts and privileges.
9. Password reset requests and temporary passwords.

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
- Validate requested permission changes on the server.

**Security Test:**

Attempt to revoke a user's document access using a non-owner account.

### Threat 4: Malicious File Upload

**Description:**

An attacker may upload executable files or harmful content disguised as permitted document formats.

**Impact:**

Malicious files may affect the application or other users who download them.

**Mitigation:**

- Restrict allowed file extensions.
- Enforce a maximum file size of 30 MB.
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
- Require authentication for protected application features.
- Apply appropriate login protections.
- Use secure session settings.

**Security Test:**

Attempt login using invalid credentials and verify that unauthorized login attempts are rejected.

### Threat 6: Password Reset Abuse

**Description:**

An attacker may submit a password reset request for another user's account or try to obtain a temporary password without authorization.

**Impact:**

An attacker may gain control of a legitimate user's account.

**Mitigation:**

- Record password reset requests for administrator review.
- Require administrators to verify the user's identity before approving a reset.
- Generate a temporary password through the administrative process.
- Share temporary passwords only through a secure channel.
- Ask users to change temporary passwords immediately.

**Security Test:**

Submit a password reset request and verify that it requires administrator processing rather than directly changing the account password.

### Threat 7: Audit Trail Tampering

**Description:**

A user may attempt to modify, delete or access audit records without authorization.

**Impact:**

Important activity records may become unreliable, reducing accountability.

**Mitigation:**

- Restrict audit trail access to authorized users.
- Record important document activities on the server.
- Store the actor, document, action and timestamp where applicable.
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

- Use Django CSRF protection.
- Include CSRF tokens in applicable forms.
- Use POST requests for sensitive operations.
- Avoid performing sensitive actions through GET requests.

**Security Test:**

Submit a sensitive POST request without a valid CSRF token and verify that it is rejected.

### Threat 9: Sensitive Information Exposure

**Description:**

Secret keys, database credentials or other sensitive configuration values may accidentally become publicly accessible.

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
- Use private file storage with authenticated access.
- Restrict direct access to uploaded documents.
- Configure database and file backups.
- Apply appropriate production security settings.

**Security Test:**

Open the deployed website in a private browser window and test document access using different user accounts.

---

## 4. Security Testing Plan

The following security tests are planned. Record actual results after executing them.

| Test ID | Security Test | Expected Result |
|---|---|---|
| ST01 | Unauthorized user accesses private document | Access denied |
| ST02 | Read user attempts to edit document | Editing denied |
| ST03 | Edit user edits an authorized document | Editing allowed |
| ST04 | Non-owner attempts to revoke access | Access denied |
| ST05 | Unsupported file upload | Upload rejected |
| ST06 | Oversized file upload | Upload rejected |
| ST07 | Invalid login attempt | Login rejected |
| ST08 | Password reset request | Administrator review required |
| ST09 | User accesses another owner's audit trail | Access denied |
| ST10 | POST request without valid CSRF token | Request rejected |

**Note:** These are planned security tests. Record the actual results after executing them. Do not mark a test as passed without evidence.

---

## 5. Risk Assessment

| Threat | Potential Impact | Priority |
|---|---|---|
| Unauthorized document access | Confidentiality loss | Critical |
| Privilege escalation | Unauthorized modification | Critical |
| Permission revocation abuse | Loss of access control | High |
| Malicious file upload | Application or user compromise | High |
| Account impersonation | Account compromise | High |
| Password reset abuse | Account compromise | High |
| Audit trail tampering | Loss of accountability | High |
| CSRF | Unauthorized actions | High |
| Sensitive information exposure | Application compromise | Critical |
| Insecure deployment and storage | Data exposure or loss | Critical |

---

## 6. Known Security Limitations

The following areas require additional verification or improvement before production deployment:

1. Malware scanning for uploaded documents.
2. Stronger file-content and MIME validation.
3. Rate limiting for login and password reset requests.
4. Private production file storage.
5. Production database and file backup configuration.
6. Additional protection for audit records.
7. Security testing of all document authorization operations.
8. Stronger password reset identity verification.
9. Mandatory password changes after temporary password resets.

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

The identified threats and security tests will be reviewed throughout development to improve the application's security and reliability. Additional testing and security improvements are necessary before using TrustVault for highly sensitive or confidential documents.

---

## 9. AI-Assisted Development: Error Identified and Corrected

During development, AI initially suggested using the local Django superuser account to access the deployed application's admin dashboard.

**What was wrong:**

The local development environment used SQLite, whereas the deployed Render application used a separate PostgreSQL database. Therefore, the local superuser account did not automatically exist in the production database.

**How I identified the issue:**

I tested the admin login on the deployed website and found that the local administrator credentials did not provide production admin access. I investigated the difference between the local and production databases.

**How I corrected it:**

1. Identified that local and production databases were separate.
2. Enabled administrator privileges for the existing authorized production user.
3. Verified that administrator login worked on the live website.
4. Removed the temporary privilege-grant command from `build.sh` after the required access was configured.
5. Verified the deployment build process without leaving the temporary privilege-grant code in the final script.

**Result:**

The production administrator login worked successfully, and the temporary deployment code was removed.

**What I learned:**

AI-generated suggestions must be checked against the actual deployment environment. Local and production databases may contain different users and data, so deployment-specific behavior must be tested rather than assumed.