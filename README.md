# TrustVault – Secure Document Sharing System

TrustVault is a Django-based web application designed to provide secure document storage and controlled document sharing. It allows users to upload documents, share them with other registered users, manage access permissions, and track document activities through an audit trail.

## Features

- **User Registration and Login:** User authentication with email OTP verification.
- **Document Upload:** Upload PDF, DOC, DOCX, and TXT files with file size validation.
- **Document Management:** View and search uploaded documents.
- **Secure Document Sharing:** Share documents with registered users.
- **Access Permissions:** Assign Read or Edit permissions to shared users.
- **Document Access Control:** Only document owners and authorized users can access documents through the application.
- **Access Revocation:** Document owners can revoke previously granted permissions.
- **Document Editing:** Users with Edit permission can edit shared documents.
- **Audit Trail:** Track document uploads, sharing, access, editing, and permission revocation.

## Technologies Used

- **Frontend:** HTML, CSS, Bootstrap
- **Backend:** Python, Django
- **Database:** SQLite
- **Email Service:** Gmail SMTP
- **Version Control:** Git and GitHub

## Project Structure

```text
TrustVault/
│
├── accounts/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── trustvault/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd TrustVault
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root and configure:

```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

Never upload your `.env` file or expose your email credentials.

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/

## Testing

Run the automated tests using:

```bash
python manage.py test accounts
```

The current test suite contains 15 tests covering important application features and access-control scenarios.

## Security Considerations

- Django password hashing and authentication.
- Email OTP verification during registration.
- File extension and file size validation.
- Permission-based document access.
- Read and Edit access controls.
- POST-based access revocation.
- CSRF protection and secure production settings configuration.

**Note:** This project is a development-stage application. Additional production security measures, including malware scanning, stronger file validation, rate limiting, private production file storage, and production database configuration, are recommended before handling sensitive real-world documents.

## Author

**Bhavya Miriyala**

B.Tech – Computer Science and Engineering (Data Science)