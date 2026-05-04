# Activity Alligator

Activity Alligator is a Flask app for organizing school activities. Students can register with their NYJC email, browse public activities, join events, and manage their own attendance. Organizers can create activities, manage participants, and export attendance data.

## What It Does

- Public activity discovery with upcoming, ongoing, and completed views
- Account registration, email verification, login, and lockout protection
- Activity creation, editing, joining, leaving, and deletion
- Attendance tracking for participants
- Reminder support for upcoming activities
- Centralized resource-layer security audit logging into Neon/Postgres

## Tech Stack

- Python + Flask
- PostgreSQL / Neon via `psycopg2`
- Flask-Login for session auth
- Flask-WTF for CSRF protection
- Resend for verification and reset emails

## Running Locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set the required environment variables:

```bash
SECRET_KEY=your-long-random-secret
DATABASE_URL=postgresql://...
RECAPTCHA_SITE_KEY=...
RECAPTCHA_SECRET_KEY=...
RESEND_API_KEY=...
MAIL_USERNAME=...
MAIL_PASSWORD=...
```

4. Start the app:

```bash
python main.py
```

The app runs on `http://localhost:5000` by default.

## Security Audit Logging

Resource-layer operations now write audit entries to Postgres so user activity is captured centrally for security review. By default the code writes to a table named `security_audit_logs`. You can override that with:

```bash
SECURITY_AUDIT_LOG_TABLE=your_existing_table_name
```

The expected table should support columns matching the inserted audit payload:

- `user_id`
- `user_email`
- `http_method`
- `request_path`
- `endpoint`
- `ip_address`
- `user_agent`
- `resource_name`
- `resource_action`
- `target_id`
- `request_metadata`

`request_metadata` is written as JSON text.
