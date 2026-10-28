# Configure Email OTP Policy

> **Module:** `base_auth_mail_otp`\
> **Model:** `res.users`\
> **Menu:** Settings > General Settings > Email OTP\
> **Actor:** user in group _Administration: Settings_

## Pre-Condition

- **Config:** An outgoing mail server is configured, so the codes can be delivered.
- **Data:** Every user that has to log in has an email address.
- **Access:** User is in group _Administration: Settings_.

## Flow

1. Open the **Settings > General Settings** menu.
2. In the left sidebar of the Settings page, click the **Email OTP** tab.
3. In **Email OTP Policy**, select **Internal users only** (portal users are not asked
   for a code) or **All users**. Leave **Disabled** to switch the feature off.
4. Fill in the limits if the defaults do not suit you:
   - **Code Validity (minutes)**: how long a code stays valid. Default 10.
   - **Maximum Wrong Attempts**: wrong codes allowed before the challenge is locked.
     Default 5.
   - **Resend Delay (seconds)**: minimum wait before a new code can be requested.
     Default 60.
   - **Maximum Emails per Hour**: codes emailed to one user within 60 minutes.
     Default 5.
5. Tick **Trusted Devices** to let users skip the code on a browser they trust, then
   fill in **Trusted Device Validity (days)**. Untick it to ask for a code at every
   login. Default is ticked, 30 days.
6. Click **Save**.

## Post-Condition

- The Email OTP settings are stored and shown again when the Settings page is reopened.
- From the next login, users covered by the selected policy are asked for a 6-digit code
  sent to their email after the password step.
