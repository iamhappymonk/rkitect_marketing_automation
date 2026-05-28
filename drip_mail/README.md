# drip_mail

Plug-in email drip automation: **Google Sheets** (signups + audit log) → **Resend** (swappable provider).

## Architecture

Each automation is a **flow** (YAML in `flows/`) that chains boxes:

1. **Source** — read contacts from Google Sheet  
2. **Trigger** — decide if a row qualifies (`on_signup`, `after_days`, `broadcast`)  
3. **Template** — render HTML + subject (Jinja2)  
4. **Send** — deliver via email provider  
5. **Audit** — write `{step_id}_status`, `_sent_at`, `_message_id`, `_error` back to the sheet  

Add a new drip by adding a template + flow YAML — no engine changes required.

## Setup

1. [Resend API key](https://resend.com/api-keys) with **Sending access** on your verified domain.
2. Google Cloud **service account** JSON; share the signup sheet with the service account email (Editor).
3. Copy `.env.example` → `.env` and fill in values.

```bash
cd drip_mail
pip install -r requirements.txt
```

Place service account JSON at path in `GOOGLE_SERVICE_ACCOUNT_JSON` (default: `./secrets/google-service-account.json`).

## Sheet columns

**Data (existing):** `Timestamp`, `Name`, `Email`, `Contact`, `Role`

**Audit (auto-added per flow):** e.g. `welcome_status`, `welcome_sent_at`, `welcome_message_id`, `welcome_error`

## Commands

From repo root:

```bash
python -m drip_mail check              # validate .env + sheet access (no sends)
python -m drip_mail list-flows
python -m drip_mail run --dry-run
python -m drip_mail run
python -m drip_mail run --watch
python -m drip_mail run --flow welcome_on_signup
```

Windows shortcuts (double-click or Task Scheduler): `scripts/run_once.bat`, `scripts/run_watch.bat`.

Or from `drip_mail/`:

```bash
python main.py run --dry-run
```

## Adding a new drip

1. Add `templates/my_email.html` + `templates/my_email.meta.yaml`
2. Add `flows/my_flow.yaml`:

```yaml
id: feedback_week1
enabled: true
step_id: feedback_week1
trigger:
  type: after_days
  days: 7
template: my_email
```

3. Run once — audit columns are appended automatically.

## Swapping email provider

Set `EMAIL_PROVIDER=resend` (default). To add another provider, implement `EmailProvider` in `providers/` and register it in `providers/__init__.py`.

## Tests

```bash
pip install -r requirements.txt
python -m pytest drip_mail/tests -v
```
