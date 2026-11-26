# View Availability on Super Calendar

> **Module:** `ssi_super_calendar`\
> **Model:** `super_calendar`\
> **Menu:** Calendar\
> **Actor:** any internal user (read-only)\
> **Inline Actions:** `action_open_source_document` (Open Source Document)

## Pre-Condition

- **Access:** User is an internal user.
- **Data:** At least one busy period exists. Periods are not entered by hand; they are
  created automatically by the documents that inherit `mixin.super_calendar_source`.
- **Module:** `ssi_super_calendar` is installed. It re-points the **Calendar** app to
  the Super Calendar.

## Flow

1. Open the **Calendar** app from the main menu. The Super Calendar opens in the
   calendar view.
2. Click the **List** button of the view switcher. The list view is displayed.
3. The list shows the busy periods of every partner.
4. Click the **Filters** button and select **Applies to Everyone**.
5. Only the periods that apply to every partner remain in the list.
6. Click a period to open its read-only form.
7. If the **Open Source Document** button is displayed in the form header, click it. The
   form of the source document opens. The button is only displayed when you can read the
   source document.

## Post-Condition

- The form of the period is displayed and cannot be edited.
- The period is shown with its real name when you can read its source document;
  otherwise it is shown as **Not available**.
- When you can read the source document, the **Source Document** field is filled and the
  **Open Source Document** button is displayed; otherwise neither is shown.
- After step 7, the form of the source document is displayed.
