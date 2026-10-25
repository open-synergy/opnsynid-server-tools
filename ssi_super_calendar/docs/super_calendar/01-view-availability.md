# View Availability on Super Calendar

> **Module:** `ssi_super_calendar`\
> **Model:** `super_calendar`\
> **Menu:** Settings > Technical > Super Calendar\
> **Actor:** any internal user (read-only)\
> **Inline Actions:** `action_open_source_document` (Open Source Document)

## Pre-Condition

- **Access:** User is an internal user and developer mode is active, because the
  **Technical** menu is only shown in developer mode.
- **Data:** At least one busy period exists. Periods are not entered by hand; they are
  created automatically by the documents that inherit `mixin.super_calendar_source`.
- **Module:** `ssi_super_calendar` is installed.

## Flow

1. Open the **Settings > Technical > Super Calendar** menu.
2. The list shows the busy periods of every partner.
3. Click the **Filters** button and select **Applies to Everyone**.
4. Only the periods that apply to every partner remain in the list.
5. Click a period to open its read-only form.
6. If the **Open Source Document** button is displayed in the form header, click it. The
   form of the source document opens. The button is only displayed when you can read the
   source document.

## Post-Condition

- The form of the period is displayed and cannot be edited.
- The period is shown with its real name when you can read its source document;
  otherwise it is shown as **Not available**.
- When you can read the source document, the **Source Document** field is filled and the
  **Open Source Document** button is displayed; otherwise neither is shown.
- After step 6, the form of the source document is displayed.
