# Kindbaby
A sharing platform for baby stuff.

## How to start the service ?

Set the following in a `.env` file at the source of the repo with the following:

```sh
export DEV_USER_EMAIL=alice
export DEV_USER_PASSWORD=xxx
POSTGRES_USER=kindbaby
POSTGRES_PASSWORD="<db_password>"
PGADMIN_EMAIL="<dbadmin_email>"
PGADMIN_PASSWORD="<dbadmin_password>"
JWT_SECRET="<jwt_secret>"
```

And run the following,

```sh
docker compose --env-file .env up
```
