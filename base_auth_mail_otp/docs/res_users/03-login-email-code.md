# Log In with an Email Code

> **Module:** `base_auth_mail_otp`\
> **Model:** `res.users`\
> **Menu:** Login page > Email Verification\
> **Actor:** user covered by the Email OTP policy\
> **Requires:** `01-configure-policy`

## Pre-Condition

- **Config:** The Email OTP policy covers the user (**Internal users only** for an
  internal user, **All users** for a portal user).
- **Record:** The user has an email address and is not exempt from the Email OTP.
- **Config:** An outgoing mail server is configured.
- **Access:** User knows the login and the password.

## Flow

1. Open the **Login page** menu entry point: there is no Odoo menu for this IK, every
   login starts on the Odoo login page.
2. Fill in **Email** and **Password**, then click **Log in**.
3. On the **Email Verification** page, open your mailbox and read the 6-digit code.
4. Type the code in **Verification Code (6 digits)**.
5. To skip the code next time on this browser, tick **Trust this device**. The box only
   appears when Trusted Devices is enabled in the Settings.
6. Click **Verify**.
7. If the code did not arrive or has expired, click **Send a new code** and use the new
   code. A new code can only be requested after the resend delay.

## Post-Condition

- The Odoo home page opens and you are logged in.
- A wrong code shows an error and sends no email. After the maximum wrong attempts the
  page shows that the code is locked and you must log in again.
- With **Trust this device** ticked, the next login on this browser skips the code until
  the trusted device validity ends.
