# Notification System Documentation

## Overview
This module handles real-time and push notifications...

## Models
### Notification
| Field | Type | Description |
|------|-----|-------------|
id | int | Primary key
title | string | Notification title
message | text | Notification body
is_read | bool | Read status

## APIs
### List Notifications
GET /api/v1/notifications/

Response:
{
  "id":1,
  "title":"Order placed",
  "is_read": false
}
