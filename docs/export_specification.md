# Excel Export Specification

## 1. Purpose

This document defines the intended structure and behavior of the Excel workbook exported by PLM Ticket Manager.

## 2. Current Workbook

Current sheets:

- `All Tickets`
- `Open Tickets`
- `Training Related`

Current data source:

- all content is generated from the application database

## 3. Current Included Columns

- `Ticket ID`
- `Subject`
- `Vendor Status`
- `Internal Status`
- `Internal Owner`
- `Vendor Issue Category`
- `Issue Category`
- `Root Cause`
- `From`
- `From Email`
- `Help Topic`
- `Priority`
- `Created Date`
- `Closed Date`
- `Comments`

## 4. Current Known Gaps

- workbook styling is basic
- date formatting is not explicitly controlled
- top row is not frozen
- filters are not applied in Excel
- the rule for `Training Related` needs business confirmation

## 5. Decisions Needed

The following points should be confirmed before refining the exporter:

- should `Training Related` remain a separate sheet
- should that sheet be based only on internal `issue_category`
- should vendor and internal categories both appear in the workbook
- which columns are essential for management review
- whether open tickets should be ordered by age, status, or priority

## 6. Recommended Next Export Standard

Recommended workbook behavior:

- freeze top row on every sheet
- apply autofilter to the header row
- format dates consistently
- use a branded header style
- keep column ordering stable across exports
- confirm sheet business rules before expanding workbook logic
