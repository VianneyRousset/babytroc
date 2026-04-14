# Graph Report - app+tests  (2026-04-11)

## Corpus Check
- 279 files · ~39,573 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1337 nodes · 4663 edges · 19 communities detected
- Extraction: 40% EXTRACTED · 60% INFERRED · 0% AMBIGUOUS · INFERRED: 2805 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `ItemRead` - 188 edges
2. `Item` - 143 edges
3. `UserPrivateRead` - 129 edges
4. `QueryFilter` - 110 edges
5. `LoanRequestState` - 109 edges
6. `QueryPageCursor` - 95 edges
7. `Joins` - 94 edges
8. `ChatId` - 91 edges
9. `LoanRequestRead` - 89 edges
10. `ApiError` - 73 edges

## Surprising Connections (you probably didn't know these)
- `Create a temporary database with alembic migrations applied.` --uses--> `Config`  [INFERRED]
  tests/fixtures/database.py → app/config.py
- `TestLoansRead` --uses--> `LoanRead`  [INFERRED]
  tests/loan/test_loans_read.py → app/schemas/loan/read.py
- `UserData` --uses--> `Config`  [INFERRED]
  tests/fixtures/items.py → app/config.py
- `ItemData` --uses--> `Config`  [INFERRED]
  tests/fixtures/items.py → app/config.py
- `Alice special item data.` --uses--> `Config`  [INFERRED]
  tests/fixtures/items.py → app/config.py

## Communities

### Community 0 - "Chat Messaging Services"
Cohesion: 0.02
Nodes (182): ChatBase, LoanBase, LoanRequestBase, ReadBase, Check `expected_message` with the websocket and REST message., Text of the many messages sent by Alice to Bob., Many messages in the same chat sent by Alice to Bob., Many chats between Alice and Bob. (+174 more)

### Community 1 - "Base Models & SQL Filters"
Cohesion: 0.02
Nodes (155): Base, borrower_id(), ChatMessageBase, CreateBase, CreationDate, DeleteBase, extract_borrower_id_from_str(), extract_item_id_from_str() (+147 more)

### Community 2 - "Loan API Queries"
Cohesion: 0.07
Nodes (134): Set loan request state to `accepted`.      Loan request state must be `pending`, Set state of given loan requests to `acceptled`.      All loan request state mus, LoanApiQuery, ChatId, DeleteQueryFilter, ItemBorrowerId, Joins, QueryFilter (+126 more)

### Community 3 - "Authentication & Errors"
Cohesion: 0.03
Nodes (103): ApiError, AuthAccountAlreadyValidatedError, AuthAccountPasswordResetAuthorization, AuthAccountPasswordResetAuthorizationNotFoundError, AuthError, AuthInvalidValidationCodeError, AuthRefreshToken, AuthRefreshTokenNotFoundError (+95 more)

### Community 4 - "App Lifecycle & Middleware"
Cohesion: 0.03
Nodes (92): DelayMiddleware, InvalidCredentialError, AuthBase, get_account_availability(), Get account availability to be created., AuthBase, BaseHTTPMiddleware, AuthConfig (+84 more)

### Community 5 - "API Query Pagination"
Cohesion: 0.06
Nodes (70): AuthAccountAvailabilityApiQuery, chat_message_query_page_cursor(), chat_query_page_cursor(), ChatApiQuery, ChatMessageApiQuery, item_matching_words_query_page_cursor(), item_query_page_cursor(), ItemApiQuery (+62 more)

### Community 6 - "Test Clients & Auth Fixtures"
Cohesion: 0.07
Nodes (47): AbstractAsyncContextManager, AuthAccountAvailability, alice_client(), bob_client(), carol_client(), client(), create_client(), login_as_user() (+39 more)

### Community 7 - "Item Test Fixtures"
Cohesion: 0.05
Nodes (44): RegionBase, RegionCreate, ItemImageBase, alice_items(), alice_items_image(), alice_many_items(), alice_new_item_images(), alice_special_item() (+36 more)

### Community 8 - "Read Services"
Cohesion: 0.04
Nodes (45): check_image_owners(), get_account_password_reset_authorization(), get_client_borrowing(), get_client_borrowing_loan_request(), get_client_chat(), get_client_chat_message_by_id(), get_client_item_by_id(), get_client_loan() (+37 more)

### Community 9 - "PubSub & Notifications"
Cohesion: 0.07
Nodes (31): AsyncIterator, BaseModel, Exception, PubsubBase, PubsubMessageNewChatMessage, PubsubMessageUpdatedAccountValidation, PubsubMessageUpdatedChatMessage, SendChatMessageBase (+23 more)

### Community 10 - "Loan Request Mutations"
Cohesion: 0.08
Nodes (32): accept_loan_request(), accept_many_loan_requests(), cancel_item_active_loan_request(), cancel_loan_request(), cancel_many_loan_requests(), reject_loan_request(), reject_many_loan_requests(), accept_client_item_loan_request() (+24 more)

### Community 11 - "Item Retrieval & Selection"
Cohesion: 0.15
Nodes (11): get_item(), get_many_items(), _normalized_word_distance(), Expression of the words match distance between `column` and `words`.      `words, Select true if the item is owned by the given `user_id`., Select true if the item is liked by the given `user_id`., Select true if the item is saved by the given `user_id`., select_liked() (+3 more)

### Community 12 - "Database Setup & Triggers"
Cohesion: 0.19
Nodes (8): create_database(), database(), define_function_notify_chat_members_new_message(), define_functions_and_triggers(), define_trigger_notify_chat_members_new_message(), drop_database(), primary_database(), Create a temporary database with alembic migrations applied.

### Community 13 - "Pagination Helpers"
Cohesion: 0.33
Nodes (5): iter_chunks(), iter_paginated_endpoint(), IterChunksStop, Iter over all pages available at `url`., grouper('abcdefgh', 3) --> ['a','b','c'], ['d','e','f'], ['g','h']

### Community 14 - "Loan Request Read Tests"
Cohesion: 0.7
Nodes (4): check_loan_request_state_active(), test_client_borrowing_requests_read_pages(), test_client_loan_requests_read_pages(), test_item_loan_requests_read_pages()

### Community 15 - "Loan Read Tests"
Cohesion: 0.67
Nodes (3): check_loan_state_active(), test_client_loans_read_pages(), TestLoansRead

### Community 16 - "Email Client"
Cohesion: 0.67
Nodes (0): 

### Community 17 - "Star Rewards"
Cohesion: 0.67
Nodes (2): Compute the number of stars won when adding `added_items_count` items., stars_gain_when_adding_item()

### Community 18 - "Test Configuration"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **17 isolated node(s):** `Insert image into the database.`, `Compute the number of stars won when adding `added_items_count` items.`, `Exception related to the API.`, `Cannot find a ressource.`, `Request conflict with the current state.` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Test Configuration`** (1 nodes): `conftest.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ItemRead` connect `Chat Messaging Services` to `Base Models & SQL Filters`, `Loan API Queries`, `API Query Pagination`, `Item Test Fixtures`, `Read Services`, `Loan Request Mutations`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **Why does `UserPrivateRead` connect `Chat Messaging Services` to `Base Models & SQL Filters`, `Test Clients & Auth Fixtures`, `Item Test Fixtures`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `Item` connect `Loan API Queries` to `Chat Messaging Services`, `Base Models & SQL Filters`, `Authentication & Errors`, `API Query Pagination`, `Item Retrieval & Selection`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 185 inferred relationships involving `ItemRead` (e.g. with `Add the specified item to client liked items.` and `List items like by client.`) actually correct?**
  _`ItemRead` has 185 INFERRED edges - model-reasoned connections that need verification._
- **Are the 138 inferred relationships involving `Item` (e.g. with `Chat` and `ChatMessage`) actually correct?**
  _`Item` has 138 INFERRED edges - model-reasoned connections that need verification._
- **Are the 126 inferred relationships involving `UserPrivateRead` (e.g. with `ReadBase` and `UserBase`) actually correct?**
  _`UserPrivateRead` has 126 INFERRED edges - model-reasoned connections that need verification._
- **Are the 106 inferred relationships involving `QueryFilter` (e.g. with `AuthRefreshTokenQueryFilter` and `AuthRefreshTokenReadQueryFilter`) actually correct?**
  _`QueryFilter` has 106 INFERRED edges - model-reasoned connections that need verification._