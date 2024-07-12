# Fetch auth token
HCP_API_TOKEN=$(curl --location "https://auth.idp.hashicorp.com/oauth2/token" \
--header "Content-Type: application/x-www-form-urlencoded" \
--data-urlencode "client_id=$HCP_CLIENT_ID" \
--data-urlencode "client_secret=$HCP_CLIENT_SECRET" \
--data-urlencode "grant_type=client_credentials" \
--data-urlencode "audience=https://api.hashicorp.cloud" | jq -r .access_token)


# Fetch secrets using curl and store the response in a variable
secrets_response=$(curl --location "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/b7c5eecc-ec58-42df-9776-1f09358cfcc2/projects/1225efbb-7bb8-4c84-bab5-0ff3302f55d7/apps/CallMinerVault/open" \
--request GET \
--header "Authorization: Bearer $HCP_API_TOKEN")

# Assuming jq is installed and the response structure matches your example
# Extract secrets and write them to a temporary .env file
echo "$secrets_response" | jq -r '.secrets[] | "\(.name)=\(.version.value)"' > .env
