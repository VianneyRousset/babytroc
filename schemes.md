# Items

- **`ItemCreate`**
  - name (`str`)
  - description (`str`)
  - images (`list[str]`)
  - regions (`list[int]`)
  - blocked by owner (`bool`)

- **`ItemPreviewRead`**
  - id (`int`)
  - name (`str`)
  - images (`list[str]`)
  - available (`bool`, computed from owner "active" and loans)
  - targeted age (`tuple[int, int]`)
  - liked by user (`bool`)
  - bookmarked by user (`bool`)

- **`ItemRead`**
  - id (`int`)
  - name (`str`)
  - description (`str`)
  - images (`list[str]`)
  - available (`bool`, computed from owner "active" and loans)
  - targeted age (`tuple[int, int]`)
  - liked by user (`bool`)
  - bookmarked by user (`bool`)
  - number of liked (`int`)
  - regions (`list[RegionRead]`)
  - owner (`UserPreviewRead`)
  - borrowings to user (`null` or `LoanPreviewRead`)
  - loans (`null` or list of `LoanPreviewRead`)
  - blocked by owner (`null` or `bool`)

# Regions

- **`RegionRead`**
  - id (`int`)
  - name (`str`)

# Users

- **`UserPreviewRead`**
  - id (`int`)
  - name (`str`)
  - avatar (`str`)
  - number of stars (`int`)
  - number of likes (`int`)

- **`UserRead`**
  - id (`int`)
  - name (`str`)
  - avatar (`str`)
  - number of stars (`int`)
  - number of likes (`int`)
  - items (`list[ItemPreviewRead]`)

- **`UserUpdate`**
  - name (`str`)
  - avatar (`str`)

# Loans

- **`LoanRead`**
  - id (`int`)
  - item (`ItemPreviewRead`)
  - borrower (`UserPreviewRead`)
  - start (date)
  - end (date or `null`)

- **`LoanRequestRead`**
  - id (`int`)
  - item (`ItemPreviewRead`)
  - message (`MessageRead`) (message sent to ask the owner)
  - creation date (`date`)

# Chat

- **`ChatListRead`**
  - chats `list[ChatRead]`
  - new messages (not marked as viewed) `list[MessageRead]`

- **`ChatRead`**
  - id (`int`)
  - borrower (`UserPreviewRead`)
  - item (`ItemPreviewRead`)

- **`MessageRead`**
  - type ("txt", "request", "request-accept", "request-refuse", "loan-start", "loan-end", "not-available", "available")
  - payload (`str`)
  - sender id (`null` or `int`)
  - receiver id (`null` or `int`)
  - client id (`int`)
  - creation date (`date`)
  - viewed (`bool`)

# Reports

- **`ReportCreate`**
  - message (`str`)
  - context (`str`)
