# Exempt a User from Email OTP

> **Module:** `base_auth_mail_otp`\
> **Model:** `res.users`\
> **Menu:** Settings > Users & Companies > Users\
> **Actor:** user in group _Administration: Settings_\
> **Requires:** `01-configure-policy`

## Pre-Condition

- **Data:** The user to exempt exists.
- **Config:** The Email OTP policy is **Internal users only** or **All users**.
- **Access:** User is in group _Administration: Settings_.

## Flow

1. Open the **Settings > Users & Companies > Users** menu.
2. Find and open the user to exempt.
3. Click the **Email OTP** tab.
4. Tick **Exempt from Email OTP**.
5. To make the exemption temporary, for example while the email server is not working,
   fill in **Exempt Until**. Leave it empty for a permanent exemption.
6. Click **Save**.

## Post-Condition

- The user logs in with the password only, without being asked for a code.
- When **Exempt Until** is filled and the date has passed, the exemption lapses by
  itself and the user is asked for a code again.
