# /utils

- **`GET /utils/avatar -> svg`**

# /items 

- **`GET /items -> list[ItemPreviewRead]`**
  - Parameters
    -terms=str
    - before=date
    - count=int
    - age=int-int
    - regions=list of integers

- **`GET /items/{id} -> ItemRead`**
- **`POST /items/{id}/report [ReportCreate]`**

# /users

- **`GET /users/{id} -> UserRead`**
- **`POST /users/{id}/report [ReportCreate]`**

# /me

- **`GET /me -> UserRead`**
- **`POST /me [UserUpdate] -> UserRead`**
- **`DELETE /me`**

# /me/saved

- **`GET /me/saved -> list[ItemPreviewRead]`**
- **`GET /me/saved/{id} -> ItemRead`**
- **`POST /me/saved/{id} -> ItemRead`**
- **`DELETE /me/saved/{id}`**

# /me/liked

- **`GET /me/liked -> list[ItemPreviewRead]`**
- **`GET /me/liked/{id} -> ItemRead`**
- **`POST /me/liked/{id} -> ItemRead`**
- **`DELETE /me/liked/{id}`**

# /me/requests

- **`GET /me/requests -> list[LoanRequestRead]`**
- **`POST /me/requests -> LoanRequestRead`**
- **`GET /me/requests/{id} -> LoanRequestRead`**
- **`DELETE /me/requests/{id}`**
- **`POST /me/requests/{id}/confirm -> LoanRead`**

# /me/borrowings

- **`GET /me/borrowings -> list[LoanRead]`**

# /me/loans

- **`GET /me/loans -> list[LoanRead]`**

# /me/items

- **`GET /me/items -> list[ItemPreviewRead]`**
- **`POST /me/items [ItemCreate] -> ItemRead`**
- **`GET /me/items/{id} -> ItemRead`**
- **`POST /me/items/{id} [ItemUpdate] -> ItemRead`**
- **`DELETE /me/items/{id}`**

- **`GET /me/items/{id}/requests -> list[LoanRequestRead]`**
- **`GET /me/items/{id}/requests/{id} -> LoanRequestRead`**
- **`POST /me/items/{id}/requests/{id}/accept`**
- **`POST /me/items/{id}/requests/{id}/reject`**

# /me/chats

- **`GET /me/chats -> ChatListRead`**
- **`GET /me/chats/ws -> websocket of ChatMessageRead`**
- **`GET /me/chats/{id} -> ChatRead`**

- **`GET /me/chats/{id}/messages -> list[ChatMessageRead]`**
  - Parameters
    - to=date
    - count=int
- **`GET /me/chats/{id}/messages -> list[ChatMessageRead]`**
- **`GET /me/chats/{id}/messages/{id} -> ChatMessageRead`**
- **`POST /me/chats/{id}/messages/{id}/see`**

- **`POST /me/chats/{id}/report [ReportCreate]`**
  - save the whole chat, who reported it, the message, the context and the creation date
