# Activity Alligator 🐊

A Flask-based activity management platform designed for NYJC students to discover, organize, and participate in school activities with centralized security auditing.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Security & Audit Logging](#security--audit-logging)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Features

### 📋 Activity Management
- **Browse Activities**: Discover public activities with filters for upcoming, ongoing, and completed events
- **Activity Organization**: Create, edit, and manage activities with full control
- **Participation**: Join and leave activities easily
- **Attendance Tracking**: Organizers can track participant attendance

### 🔐 User Management
- **Email Registration**: NYJC email verification for secure account creation
- **Authentication**: Secure login with session management via Flask-Login
- **Account Security**: Login lockout protection and password reset functionality
- **Email Notifications**: Automated reminders for upcoming activities

### 📊 Security Features
- **Resource-Layer Audit Logging**: Centralized security logging to PostgreSQL
- **CSRF Protection**: Flask-WTF integration for form security
- **Content Security**: reCAPTCHA protection and profanity filtering

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Python + Flask 3.0.0 |
| **Database** | PostgreSQL (via Neon) |
| **ORM/Database Driver** | psycopg2-binary 2.9.10 |
| **Authentication** | Flask-Login 0.6.3 |
| **Security** | Flask-WTF 1.2.1, reCAPTCHA |
| **Email Service** | Resend 0.7.0 |
| **Content Processing** | Markdown 3.5.2, Bleach 6.1.0 |
| **Deployment** | Gunicorn 21.2.0 |
| **Utilities** | python-dotenv 1.0.0, python-dateutil 2.8.2, better-profanity 0.7.0 |

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL database (or Neon account)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/nyjc-computing-2526/Capstone-Project-2527.git
   cd Capstone-Project-2527
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-long-random-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@host:port/database_name

# Security - reCAPTCHA
RECAPTCHA_SITE_KEY=your-recaptcha-site-key
RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key

# Email Service - Resend
RESEND_API_KEY=your-resend-api-key

# Email Authentication (optional backup)
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password

# Security Audit Logging (optional)
ENABLE_RESOURCE_AUDIT_LOGGING=true
SECURITY_AUDIT_LOG_TABLE=audit_logs
```

### Generating SECRET_KEY

Generate a secure random key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Running Locally

1. **Ensure environment variables are set** (see [Configuration](#configuration))

2. **Start the application**
   ```bash
   python main.py
   ```

3. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

### Development Mode

For development with auto-reload:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python main.py
```

## Security & Audit Logging

Activity Alligator includes a comprehensive security audit logging system that tracks all resource-level access to PostgreSQL.

### How It Works

- Each request writes a single audit entry to your PostgreSQL database
- Captures user activity without duplicate entries during a single page load
- Enables security review and compliance tracking

### Setup

1. **Enable audit logging** in your `.env`:
   ```bash
   ENABLE_RESOURCE_AUDIT_LOGGING=true
   SECURITY_AUDIT_LOG_TABLE=audit_logs
   ```

2. **Create the audit table** with the following schema:
   ```sql
   CREATE TABLE audit_logs (
       id SERIAL PRIMARY KEY,
       user_id INTEGER,
       user_email VARCHAR(255),
       http_method VARCHAR(10),
       request_path TEXT,
       endpoint VARCHAR(255),
       ip_address VARCHAR(45),
       user_agent TEXT,
       resource_name VARCHAR(255),
       resource_action VARCHAR(100),
       target_id INTEGER,
       request_metadata JSONB,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### Audit Log Columns

| Column | Description |
|--------|-------------|
| `user_id` | ID of the user making the request |
| `user_email` | Email address of the user |
| `http_method` | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `request_path` | Full path of the request |
| `endpoint` | Flask endpoint name |
| `ip_address` | Client IP address |
| `user_agent` | Browser/client user agent string |
| `resource_name` | Name of the resource being accessed |
| `resource_action` | Action performed (create, read, update, delete) |
| `target_id` | ID of the target resource |
| `request_metadata` | Additional request data (stored as JSON) |

## Project Structure

```
Capstone-Project-2527/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── README.md              # This file
├── app/
│   ├── __init__.py
│   ├── models/            # Database models
│   ├── routes/            # Flask route blueprints
│   ├── forms/             # WTForms form definitions
│   ├── utils/             # Utility functions
│   └── templates/         # Jinja2 HTML templates
├── static/                # CSS, JavaScript, images
└── migrations/            # Database migrations (if applicable)
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Commit your changes: `git commit -m 'Add some feature'`
3. Push to the branch: `git push origin feature/your-feature-name`
4. Open a Pull Request

## License

This project is part of the NYJC Capstone Project 2526-2527.

## Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/nyjc-computing-2526/Capstone-Project-2527/issues).
