# System Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The System Controller handles general system operations, such as sending feedback, reporting exceptions, and retrieving system information (version, update status).

## Key Endpoints

### `POST /system/feedback`
Sends user feedback to the engine team.
- **Input**: `FeedbackRequestJson`
- **Requires Auth**: Yes

### `POST /system/report-exception`
Reports a crash or exception with logs.
- **Input**: `ReportExceptionRequestJson`
- **Requires Auth**: Yes

### `POST /system/general-info`
Returns general system info (engine version, Python version, OS, etc.).
- **Requires Auth**: Yes
