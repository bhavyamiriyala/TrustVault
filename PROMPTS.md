AI Prompt and Correction Log – TrustVault
This file documents how AI tools were used during the development of TrustVault. It records the prompts, AI-generated suggestions, mistakes identified, corrections made, and related Git commits.

AI was used as a development assistant. All generated code and suggestions were reviewed and tested before being accepted.

## Entry 1 – Repository Security and Submission Rules
**Date:** 1 November 2026
**Task:** Understand the GitHub repository visibility requirements.

**Prompt given:**
"Review the Snovasys hiring challenge instructions and explain how I should manage my GitHub repository without violating their source-code confidentiality rules."

**AI output:**
Initially, AI suggested keeping the repository public because the submission required a public GitHub link.

**What was wrong:**
The initial recommendation was based on incomplete instructions. The official invitation clearly stated that the repository must not be made public before the deadline.

**What I did:**
I shared the complete official instructions, identified the contradiction, and changed the GitHub repository visibility to Private. I will confirm with the college placement cell when to make it public for evaluation.

**Related commit**: No code commit. This was a repository visibility change.

## Entry 2 – Authorization and Access Control

**Date:** 2 November 2026

**Task:** Review document ownership and authorization to prevent unauthorized users from accessing private documents.

**Prompt given:**

"Act as a Django security reviewer. Review my TrustVault document access logic. Check whether document owners and users with sharing permissions are authorized correctly. Verify that an unauthorized user cannot download or view another user's document by changing the document ID or URL. Check whether authorization is enforced on the server side. Identify any security weaknesses and suggest corrections."

**AI output:**

AI recommended reviewing document ownership checks, shared-user permissions and server-side authorization. It also suggested testing direct document URLs with different user accounts.

**What was wrong:**

The actual implementation has not yet been reviewed against all these security scenarios. No specific authorization bug has been confirmed yet.

**What I did:**

Planned to inspect the Django views responsible for document access and verify that only the owner or an authorized shared user can access a document.

**Test evidence:**

Pending security testing with document owners, authorized users and unauthorized users.

**Related commit:** To be added after implementing and committing any verified corrections.

---

## Entry 3 – Read and Edit Permissions

**Date:** 4 November 2026 (Evening)

**Task:** Verify that Read and Edit permissions are correctly enforced.

**Prompt given:**

"Review the Read and Edit permission implementation in my TrustVault Django application. Check whether a user with Read permission can only view or download a shared document and cannot modify it. Check whether a user with Edit permission can modify the document. Also verify that the document owner retains control. Identify possible privilege escalation issues and suggest secure server-side corrections."

**AI output:**

AI suggested checking permissions separately for viewing, downloading, editing and other document operations. It recommended enforcing permission checks inside Django views rather than relying only on frontend buttons.

**What was wrong:**

No specific implementation error has been confirmed yet. The existing permission logic needs to be checked against all the expected user roles.

**What I did:**

Planned to verify the existing permission checks and test Read-only and Edit users separately. Any confirmed issues will be corrected and documented.

**Test evidence:**

Pending:

- Read user attempting to edit a document.
- Edit user modifying an authorized shared document.
- User attempting to edit a document without permission.

**Related commit:** To be added after verified corrections.

---

## Entry 4 – Audit Trail Security

**Date:** 5 November 2026

**Task:** Review audit logging and prevent unauthorized access to activity records.

**Prompt given:**

"Act as a security reviewer for my TrustVault Django application. Review the AuditLog model and audit trail views. Check whether upload, share, access, edit and revoke activities are recorded correctly with the appropriate user, document and timestamp. Verify that one user cannot view or modify another document owner's audit records. Identify missing audit events or authorization weaknesses and suggest improvements."

**AI output:**

AI recommended checking whether important document activities are recorded and whether audit trail access is restricted to authorized users. It also suggested verifying that the actor, document and timestamp are stored correctly.

**What was wrong:**

The actual audit implementation has not yet been fully reviewed. Missing events or authorization problems must be identified through code inspection and testing.

**What I did:**

Planned to inspect the AuditLog model and audit trail view, verify ownership restrictions and test access using different accounts.

**Test evidence:**

Pending:

- Verify that document activities create audit records.
- Attempt to view another owner's audit trail.
- Check whether unauthorized users can modify audit records.

**Related commit:** To be added after verified corrections.

---

## Entry 5 – Testing and Error Handling

**Date:** 5 November 2026

**Task:** Review application tests, input validation and error handling.

**Prompt given:**

"Review the existing Django tests and error handling in my TrustVault application. Check document upload validation, unsupported file extensions, file size restrictions, login authentication, OTP verification, unauthorized document access and permission-related operations. Identify missing test cases, incorrect assumptions and possible security issues. Suggest additional tests and explain how to verify them."

**AI output:**

AI recommended checking both successful and unsuccessful application scenarios. It suggested testing invalid file uploads, unauthorized access, permission restrictions and authentication failures.

**What was wrong:**

The existing test cases need to be executed to confirm that they pass. Additional security scenarios may also be required. No new test failure is being claimed at this stage.

**What I did:**

Planned to execute the Django test suite, review any failures and add tests for missing security scenarios. Corrections will be made based on actual test results.

**Test evidence:**

Pending execution of:

`python manage.py test accounts`

**Related commit:** To be added after completing testing and committing any corrections.

---

## AI Usage Declaration

AI tools were used to assist with development, debugging, code review, documentation and testing.

I reviewed the generated suggestions, checked the implementation, corrected identified problems and tested the application. I take responsibility for understanding the code and the final submitted implementation.
