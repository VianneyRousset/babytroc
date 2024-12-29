# /utils

- **`GET /utils/avatar -> svg`**

# /items 

 - X **`GET /items -> list[ItemPreviewRead]`**
-  X **`GET /items/{id} -> ItemRead`**
- **`POST /items/{id}/report [ReportCreate]`**

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
- **`POST /me/saved/{id} -> ItemRead`**
- **`DELETE /me/saved/{id}`**

# /me/liked

- X **`GET /me/liked -> list[ItemPreviewRead]`**
- X **`GET /me/liked/{id} -> ItemRead`**
- **`POST /me/liked/{id} -> ItemRead`**
- **`DELETE /me/liked/{id}`**

# /me/requests

- X **`GET /me/requests -> list[LoanRequestRead]`**
- **`POST /me/requests [LoanRequestCreate] -> LoanRequestRead`**
- X **`GET /me/requests/{id} -> LoanRequestRead`**
- **`DELETE /me/requests/{id}`**
- **`POST /me/requests/{id}/confirm -> LoanRead`**

# /me/borrowings

- **`GET /me/borrowings -> list[LoanRead]`**

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

- **`GET /me/chats -> ChatListRead`**
- **`GET /me/chats/ws -> websocket of ChatMessageRead`**
  - populate websocket with unsee messages
- **`GET /me/chats/{id} -> ChatRead`**

- **`GET /me/chats/{id}/messages -> list[ChatMessageRead]`**
  - Parameters
    - to=date
    - count=int
- **`GET /me/chats/{id}/messages -> list[ChatMessageRead]`**
- **`POST /me/chats/{id}/messages -> ChatMessageRead`**
- **`GET /me/chats/{id}/messages/{id} -> ChatMessageRead`**
- **`POST /me/chats/{id}/messages/{id}/see`**

- **`POST /me/chats/{id}/report [ReportCreate]`**
  - save the whole chat, who reported it, the message, the context and the creation date
