# /utils

- **`GET /utils/avatar -> svg`**

# /items 

 - X **`GET /items -> list[ItemPreviewRead]`**
-  X **`GET /items/{id} -> ItemRead`**
- **`POST /items/{id}/report [ReportCreate]`**
- X **`POST /items/{id}/request`**
- X **`DELETE /items/{id}/request`**

# /users

- X **`GET /users/{id} -> UserRead`**
- **`POST /users/{id}/report [ReportCreate]`**
- X **`GET /users/{user_id}/items -> list[ItemPreviewRead]`**
- X **`GET /users/{user_id}/items/{item_id} -> ItemRead`**

# /me

- X **`GET /me -> UserRead`**
- **`POST /me [UserUpdate] -> UserRead`**
- **`DELETE /me`**

# /me/saved

- X **`GET /me/saved -> list[ItemPreviewRead]`**
- X **`GET /me/saved/{id} -> ItemRead`**
- X **`POST /me/saved/{id} -> ItemRead`**
- X **`DELETE /me/saved/{id}`**

# /me/liked

- X **`GET /me/liked -> list[ItemPreviewRead]`**
- X **`GET /me/liked/{id} -> ItemRead`**
- X **`POST /me/liked/{id} -> ItemRead`**
- X **`DELETE /me/liked/{id}`**

# /me/borrowings

- X **`GET /me/borrowings -> list[LoanRead]`**

# /me/loans

- **`GET /me/loans -> list[LoanRead]`**

# /me/items

- X **`GET /me/items -> list[ItemPreviewRead]`**
- **`POST /me/items [ItemCreate] -> ItemRead`**
- X **`GET /me/items/{id} -> ItemRead`**
- **`POST /me/items/{id} [ItemUpdate] -> ItemRead`**
- **`DELETE /me/items/{id}`**

- X **`GET /me/items/{id}/requests -> list[LoanRequestRead]`**
- X **`GET /me/items/{id}/requests/{id} -> LoanRequestRead`**
- **`POST /me/items/{id}/requests/{id}/accept`**
- **`POST /me/items/{id}/requests/{id}/reject`**

# /me/chats

- X **`GET /me/chats -> ChatListRead`**
- **`GET /me/chats/ws -> websocket of ChatMessageRead`**
  - populate websocket with unsee messages
- X **`GET /me/chats/{id} -> ChatRead`**

- X **`GET /me/chats/{id}/messages -> list[ChatMessageRead]`**
  - Parameters
    - to=date
    - count=int
- X **`GET /me/chats/{id}/messages -> list[ChatMessageRead]`**
- **`POST /me/chats/{id}/messages -> ChatMessageRead`**
- X **`GET /me/chats/{id}/messages/{id} -> ChatMessageRead`**
- **`POST /me/chats/{id}/messages/{id}/see`**

- **`POST /me/chats/{id}/report [ReportCreate]`**
  - save the whole chat, who reported it, the message, the context and the creation date
