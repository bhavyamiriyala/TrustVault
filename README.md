# TrustVault – Secure Document Sharing System

TrustVault is a Django-based web application designed to provide secure document storage and controlled document sharing. It allows registered users to upload documents, share them with other users, manage access permissions, and track document activities through an audit trail.

**Live Website:** https://trustvault-wscr.onrender.com

**GitHub Repository:** https://github.com/bhavyamiriyala/TrustVault

## Features

### User Authentication
- User registration with username, email, and password.
- Secure login and logout.
- Django-based password hashing and authentication.
- Separate administrator login through Django Admin.
- Admin-assisted forgot password request system.
- Users can change their passwords after login.

### Document Management
- Upload PDF, DOC, DOCX, and TXT files.
- Maximum file upload size: 30 MB.
- File extension, content, and size validation.
- View and search uploaded documents.
- Edit documents based on access permissions.

### Secure Document Sharing
- Share documents with registered users.
- Assign Read or Edit permissions.
- Only document owners and authorized users can access documents through the application.
- Document owners can revoke previously granted permissions.

### Audit Trail
Track important document activities, including:
- Document uploads.
- Document sharing.
- Document access.
- Document editing.
- Permission revocation.

### Administrator Features
- Django Admin dashboard.
- Manage documents, sharing permissions, and audit logs.
- View password reset requests.
- Generate temporary passwords for verified password reset requests.

## Technologies Used

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, Bootstrap |
| Backend | Python, Django |
| Local Database | SQLite |
| Production Database | PostgreSQL |
| Deployment | Render |
| Static Files | WhiteNoise |
| Version Control | Git and GitHub |

## Project Structure

```text
TrustVault/
│
├── accounts/
│   ├── migrations/
│   ├── templates/
│   │   └── accounts/
│   ├── admin.py
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
├── build.sh
├── manage.py
├── requirements.txt
├── .gitignore
├── PROMPTS.md
├── THREATS.md
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/bhavyamiriyala/TrustVault.git
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

Create a `.env` file in the project root and configure the variables required by `trustvault/settings.py`.

Example:

```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Never upload your `.env` file or expose secret keys and credentials.

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your administrator account.

### 8. Run the development server

```bash
python manage.py runserver
```

Open the application:

http://127.0.0.1:8000/

## Administrator Access

The administrator dashboard is available at:

https://trustvault-wscr.onrender.com/admin/

Administrators can manage application records and review password reset requests.

For security, administrators should verify a user's identity before generating and sharing a temporary password. Temporary passwords should be shared through a verified secure channel.

## Deployment

TrustVault is deployed using Render.

**Live Application:** https://trustvault-wscr.onrender.com

The deployment process uses `build.sh` to:
- Install Python dependencies.
- Collect static files.
- Apply database migrations.

The production environment uses PostgreSQL.

**Note:** The free Render instance may spin down after inactivity, so the first request can take additional time to load.

## Testing

Run the automated tests using:

```bash
python manage.py test accounts
```

The current test suite contains **20 automated tests** covering important application features, authentication, document operations, and access-control scenarios.

Run Django system checks using:

```bash
python manage.py check
```

## Security Considerations

- Django password hashing and authentication.
- CSRF protection for forms and state-changing requests.
- File extension, content, and file size validation.
- Maximum upload size of 30 MB.
- Permission-based document access.
- Read and Edit access controls.
- POST-based access revocation.
- Audit logging of important document activities.
- Environment-based configuration for sensitive settings.

### Future Security Improvements

- Malware scanning for uploaded documents.
- Stronger file content validation.
- Login and password-reset rate limiting.
- Private production file storage with protected downloads.
- Improved administrator identity verification.
- Additional security monitoring and testing.

**Security Note:** TrustVault is a fresher hiring challenge project and should receive additional security testing and hardening before being used to store sensitive real-world documents.

## Author

**Bhavya Miriyala**

B.Tech – Computer Science and Engineering (Data Science)