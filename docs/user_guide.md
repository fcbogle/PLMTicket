# PLM Ticket Manager User Guide

## 1. Purpose

PLM Ticket Manager is used to:

- upload vendor PLM support ticket CSV files
- review imported tickets
- add internal categorisation and notes
- export an Excel workbook for management review

## 2. What The System Does

The application keeps two kinds of data:

- vendor data imported from the CSV
- internal data entered by Blatchford users

Important:

- vendor data can be refreshed by re-uploading a CSV
- internal data is preserved when tickets are re-imported

## 3. Main Screen Overview

The main screen has four areas:

- top bar with branding and the Excel export button
- import and filter section
- ticket list on the left
- ticket detail and internal entry form on the right

## 4. Uploading A CSV File

1. Open the application in your browser.
2. In the `Import And Filter` section, choose the vendor CSV file.
3. Select `Upload CSV`.
4. Wait for the import message to appear.

Expected result:

- new tickets are added
- existing tickets are updated with vendor data
- internal classifications and comments remain in place

## 5. Finding Tickets

Use the filter controls to narrow the ticket list.

Available options:

- search by ticket ID or subject text
- filter by status
- filter by category

Actions:

- choose `Apply` to refresh the list using the current filters
- choose `Clear` to remove filters and reload all tickets

## 6. Reviewing A Ticket

1. Select a ticket from the list on the left.
2. Review the vendor details shown in the right-hand panel.

The detail panel shows key vendor information such as:

- ticket ID
- vendor status
- assigned agent
- vendor category
- raised by
- closed date
- subject

## 7. Updating Internal Fields

For the selected ticket, update the internal fields:

- `Internal Status`
- `Internal Owner`
- `Issue Category`
- `Root Cause`
- `Comments`

Then:

1. Choose `Save Internal Fields`.
2. Wait for the on-screen confirmation message.

Expected result:

- the application shows a save confirmation
- the internal values remain attached to the ticket
- those internal values are preserved after later CSV imports

## 8. Exporting Excel

1. Choose `Export Excel` from the top bar.
2. Open the downloaded workbook.
3. Review the workbook sheets for management reporting.

Current workbook sheets:

- `All Tickets`
- `Open Tickets`
- `Training Related`

## 9. Important Data Note

Your changes are stored in the application database, not in the CSV file.

This means:

- saving a ticket updates the application data
- re-uploading the CSV does not remove your internal notes and categorisation
- changing the CSV alone does not update internal fields

## 10. Current Limitations

- the app currently assumes a known vendor CSV format
- user login is not implemented yet
- category and status dropdown values are currently fixed
- Excel formatting is still basic and may be refined later

## 11. Good Practice For Users

- upload the latest vendor CSV before starting a review cycle
- use consistent internal status values
- use comments for context that would help management or later reviewers
- avoid putting temporary notes into root cause if they belong in comments

## 12. Support Notes

If you notice:

- a CSV does not import correctly
- expected internal notes are missing
- the workbook content does not match expectations

record:

- the CSV filename
- the ticket number affected
- the action being taken when the issue occurred

This will make troubleshooting faster.
