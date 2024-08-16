## Prerequisites

- Docker and Docker Compose

## Deploy the server

1. Environment variables
   - Create `.env` file with env vars listed in `.env.example`
2. Start the server
   - Run `docker compose up -d`
   - Alternatively, you can use another Mongo instance by setting the corresponding Mongo related environment variables and running `docker compose up be -d`
