# Chatting System Documentation

## Overview
This module handles real-time one-to-one chatting between users using
Django REST Framework and Django Channels (WebSockets).

It supports:
- Text messaging
- Real-time delivery
- Message persistence in database

---
## Models

### Conversation
| Field | Type | Description |
|------|-----|-------------|
id | int | Primary key
user_1 | FK(User) | First participant
user_2 | FK(User) | Second participant
created_at | datetime | Conversation creation time

---

### Message
| Field | Type | Description |
|------|-----|-------------|
id | int | Primary key
conversation | FK(Conversation) | Related conversation
sender | FK(User) | Message sender
content | text | Message body
is_read | boolean | Read status
created_at | datetime | Sent time

---

## REST APIs

### List Conversations
GET /api/v1/chat/conversations/

Response:
```json
[
  {
    "id": 1,
    "user": "Seller A",
    "last_message": "Hello"
  }
]
