# PLM Ticket Manager Azure Deployment Guide

## 1. Purpose

This document describes a practical Azure deployment approach for `PLM_Tickets`, based on the deployment shape already used for `rfp_rag_assistant`.

It covers:

- initial deployment
- current deployment readiness gaps
- local data promotion
- backend-only updates
- frontend-only updates
- coordinated full releases

## 2. Recommended Deployment Shape

Use the same split that worked well for `rfp_rag_assistant`:

### Backend

Deploy the FastAPI backend as a Docker image to Azure Container Apps.

### Frontend

Build the Vite frontend and deploy the static output to Azure Static Web Apps.

### Container Registry

Use Azure Container Registry to store backend images.

### Persistence

For this application, persistence matters because ticket enrichment is user-entered data.

For the current expected volume, the recommended deployment path is:

1. SQLite with persistent mounted storage in Azure Container Apps
2. PostgreSQL later only if requirements grow or operational needs justify it

## 3. Important Difference From `rfp_rag_assistant`

`rfp_rag_assistant` is much closer to stateless deployment. `PLM_Tickets` is not, because it stores live ticket and enrichment data in the application database.

That means deployment for `PLM_Tickets` must explicitly address:

- database location
- database persistence
- migration of your current local SQLite data

## 4. Current Repo Readiness Gaps

Before a clean Azure deployment, the current codebase should be adjusted in a few places.

### 4.1 Backend database URL is hard-coded

Current code in [database.py](/Users/frankbogle/PycharmProjects/PLM_Tickets/backend/app/database.py:1):

- `DATABASE_URL = "sqlite:///./plm_tickets.db"`

This should become environment-driven so deployment can use:

- mounted SQLite path such as `sqlite:////data/plm_tickets.db`
- or PostgreSQL

### 4.2 Backend CORS is hard-coded for local development

Current code in [main.py](/Users/frankbogle/PycharmProjects/PLM_Tickets/backend/app/main.py:20):

- `allow_origins=["http://localhost:5173"]`

This should be moved into an environment variable so Azure frontend URLs can be allowed.

### 4.3 Frontend API base URL is hard-coded

Current code in [App.tsx](/Users/frankbogle/PycharmProjects/PLM_Tickets/frontend/src/App.tsx:27):

- `const API_BASE = "http://localhost:8000";`

This should be replaced with a Vite environment variable such as:

- `import.meta.env.VITE_API_BASE_URL`

### 4.4 No backend Dockerfile exists yet

Unlike `rfp_rag_assistant`, this repo does not yet include a backend Dockerfile or image build path.

### 4.5 Current backend startup is local-only

Current local startup:

- `uvicorn app.main:app --reload`

For Azure Container Apps, the production command should bind to `0.0.0.0` and use `${PORT:-8000}`.

## 5. Recommended Deployment Decision

### 5.1 Recommended Low-Cost Deployment

For this application as it stands now, use:

- SQLite
- Azure Container Apps for the backend
- Azure File Share mounted into the backend container
- Azure Static Web Apps for the frontend

Reason:

- very low ticket volume
- simplest application design
- lowest likely Azure cost
- no immediate need to introduce PostgreSQL complexity

### 5.2 When To Revisit PostgreSQL

Move to PostgreSQL later if one or more of these become true:

- multiple concurrent users become common
- reporting/query complexity grows significantly
- you need stronger managed backup/restore workflows
- the mounted SQLite file becomes an operational concern

## 6. Initial Deployment Plan

## 6.1 Prerequisites

- `az login`
- Docker installed and running
- Node.js and `npm`
- Python 3.11 environment available locally
- repo in the exact state you intend to deploy

Deploy from:

```text
/Users/frankbogle/PycharmProjects/PLM_Tickets
```

## 6.2 Azure Resources

Recommended resources:

- Resource Group
- Azure Container Registry
- Azure Container Apps Environment
- Azure Container App for backend
- Azure Static Web App for frontend

Required for the recommended SQLite path:

- Azure File Share for persistent database storage

## 6.3 Shell Variables

Example values:

```sh
RG="rg-plm-ticket-manager"
LOC="uksouth"
ACR="acrplmticket$(date +%s)"
APPENV="aca-env-plm-ticket"
APP="plm-ticket-api"
IMAGE_REPO="plm-ticket-manager"
IMAGE_TAG="v1"
```

## 6.4 Clear Azure CLI default group

Recommended:

```sh
az configure --defaults group=""
```

Then always pass `-g "$RG"` explicitly.

## 6.5 Register Providers

```sh
az provider register -n Microsoft.ContainerRegistry --wait
az provider register -n Microsoft.App --wait
az provider register -n Microsoft.OperationalInsights --wait
```

## 6.6 Create Resource Group And ACR

```sh
az group create -n "$RG" -l "$LOC"
az acr create -g "$RG" -n "$ACR" --sku Basic
```

## 6.7 Enable ACR Admin And Log Docker In

```sh
az acr update -g "$RG" -n "$ACR" --admin-enabled true

LOGIN_SERVER=$(az acr show -g "$RG" -n "$ACR" --query loginServer -o tsv)
ACR_USER=$(az acr credential show -g "$RG" -n "$ACR" --query username -o tsv)
ACR_PASS=$(az acr credential show -g "$RG" -n "$ACR" --query "passwords[0].value" -o tsv)

docker login "$LOGIN_SERVER" -u "$ACR_USER" -p "$ACR_PASS"
```

## 7. Pre-Deployment Code Work That Should Be Done First

Before using Azure in earnest, make these code changes in this repo:

1. Move backend `DATABASE_URL` into environment configuration
2. Move backend CORS origins into environment configuration
3. Move frontend API base URL into `VITE_API_BASE_URL`
4. Add a backend Dockerfile
5. Decide whether SQLite or PostgreSQL is the deployment database

These are not optional if you want a clean repeatable deployment.

## 8. Suggested Backend Dockerfile

For this project, a simple backend-only Dockerfile should look broadly like this:

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY backend/app /app/app
COPY frontend/public /app/frontend/public

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

Note:

- the exporter uses logo files from `frontend/public`
- those assets therefore need to be available in the backend image

## 9. Initial Backend Deployment

## 9.1 Build And Push The Backend Image

Azure Container Apps expects `linux/amd64`.

Run from the repo root:

```sh
cd /Users/frankbogle/PycharmProjects/PLM_Tickets

docker buildx build --platform linux/amd64 \
  -f backend/Dockerfile \
  -t "$LOGIN_SERVER/$IMAGE_REPO:$IMAGE_TAG" \
  --push .
```

## 9.2 Create The Container Apps Environment

```sh
az containerapp env create -g "$RG" -n "$APPENV" -l "$LOC"
```

## 9.3 Create Azure Storage For SQLite Persistence

Create a storage account and file share for the database file.

Example:

```sh
STORAGE="stplmticket$(date +%s)"
SHARE="plmdata"

az storage account create -g "$RG" -n "$STORAGE" -l "$LOC" --sku Standard_LRS
STORAGE_KEY=$(az storage account keys list -g "$RG" -n "$STORAGE" --query "[0].value" -o tsv)

az storage share-rm create -g "$RG" --storage-account "$STORAGE" -n "$SHARE"
```

## 9.4 Copy Your Current Local Database Into Azure Storage

This is the critical step that preserves the ticket enrichment you have already entered locally.

Current local database:

- `backend/plm_tickets.db`

Upload it into the file share before the app goes live:

```sh
cd /Users/frankbogle/PycharmProjects/PLM_Tickets

az storage file upload \
  --account-name "$STORAGE" \
  --account-key "$STORAGE_KEY" \
  --share-name "$SHARE" \
  --source backend/plm_tickets.db \
  --path plm_tickets.db
```

This ensures the deployed backend starts with your real ticket data rather than an empty database.

## 9.5 Create The Backend Container App

```sh
az containerapp create -g "$RG" -n "$APP" \
  --environment "$APPENV" \
  --image "$LOGIN_SERVER/$IMAGE_REPO:$IMAGE_TAG" \
  --target-port 8000 \
  --ingress external \
  --registry-server "$LOGIN_SERVER" \
  --registry-username "$ACR_USER" \
  --registry-password "$ACR_PASS" \
  --env-vars PLM_DATABASE_URL="sqlite:////data/plm_tickets.db" PLM_CORS_ALLOWED_ORIGINS="http://localhost:5173"
```

Get the backend FQDN:

```sh
BACKEND_FQDN=$(az containerapp show -g "$RG" -n "$APP" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo "$BACKEND_FQDN"
```

## 9.6 Mount The Azure File Share Into The Container App

Add the Azure File Share as storage for the Container App environment and mount it into the backend container at `/data`.

Example sequence:

```sh
az containerapp env storage set -g "$RG" -n "$APPENV" \
  --storage-name plmdata \
  --azure-file-account-name "$STORAGE" \
  --azure-file-account-key "$STORAGE_KEY" \
  --azure-file-share-name "$SHARE" \
  --access-mode ReadWrite
```

Then update the app template to mount the storage:

```sh
az containerapp update -g "$RG" -n "$APP" \
  --set template.volumes[0].name=plmdata \
  --set template.volumes[0].storageType=AzureFile \
  --set template.volumes[0].storageName=plmdata \
  --set template.containers[0].volumeMounts[0].volumeName=plmdata \
  --set template.containers[0].volumeMounts[0].mountPath=/data \
  --set-env-vars PLM_DATABASE_URL="sqlite:////data/plm_tickets.db"
```

Important:

- the mounted database path must match the uploaded filename
- the backend must use `sqlite:////data/plm_tickets.db`
- if the app starts before the file is mounted correctly, it may create a new empty local SQLite file inside the container

## 10. Initial Frontend Deployment

## 10.1 Create The Static Web App

In Azure Portal:

1. Create `Static Web App`
2. Use resource group `rg-plm-ticket-manager`
3. Choose `Free` or higher
4. For deployment source, choose `Other`

After creation, note:

- production URL
- preview URL if Azure provides one

## 10.2 Build The Frontend

Once `VITE_API_BASE_URL` support exists, build with the backend URL:

```sh
cd /Users/frankbogle/PycharmProjects/PLM_Tickets/frontend

VITE_API_BASE_URL="https://$BACKEND_FQDN" npm run build
```

## 10.3 Publish `frontend/dist`

Deploy the generated `frontend/dist` output to Azure Static Web Apps using your preferred upload/release path.

## 11. Environment Variables For PLM Ticket Manager

Recommended backend environment variables:

```env
PLM_DATABASE_URL=sqlite:////data/plm_tickets.db
PLM_CORS_ALLOWED_ORIGINS=https://your-app.azurestaticapps.net,https://your-app-preview.uksouth.azurestaticapps.net,http://localhost:5173
```

Recommended frontend build variable:

```env
VITE_API_BASE_URL=https://your-backend-fqdn
```

## 12. Data Promotion For Initial Deployment

This is the part that matters most for `PLM_Tickets`.

Your current enriched data lives in:

- `backend/plm_tickets.db`

If you do not migrate this data, the deployed app will not contain your internal notes and classifications.

## 12.1 Recommended Current Data Migration Steps

Use this exact order:

1. Stop making local edits just before the cutover window.
2. Back up the current local file:

```sh
cp backend/plm_tickets.db backend/plm_tickets.predeploy.backup.db
```

3. Upload `backend/plm_tickets.db` to the Azure File Share.
4. Mount the Azure File Share at `/data`.
5. Set:

```text
PLM_DATABASE_URL=sqlite:////data/plm_tickets.db
```

6. Start or restart the backend Container App.
7. Validate known tickets and comments in the deployed UI.

## 12.2 Minimum Validation After Data Promotion

Check:

- total ticket count
- known ticket IDs
- known internal comments
- known issue categories
- one or two recent updates you personally entered locally
- Excel export behavior

## 13. Initial Go-Live Checklist

1. Backend image deployed successfully
2. Frontend deployed successfully
3. CORS configured for real frontend origins
4. Database path/connection configured correctly
5. Existing ticket data promoted successfully from `backend/plm_tickets.db`
6. `/health` returns `ok`
7. CSV upload works
8. Ticket update works
9. Excel export works

## 14. Backend-Only Update Procedure

Use this when only backend code changes.

### 14.1 Build A New Image Tag

Always use a new image tag:

```sh
IMAGE_TAG="v2"
```

### 14.2 Build And Push

```sh
cd /Users/frankbogle/PycharmProjects/PLM_Tickets

docker buildx build --platform linux/amd64 \
  -f backend/Dockerfile \
  -t "$LOGIN_SERVER/$IMAGE_REPO:$IMAGE_TAG" \
  --push .
```

### 14.3 Update The Container App

```sh
az containerapp update -g "$RG" -n "$APP" \
  --image "$LOGIN_SERVER/$IMAGE_REPO:$IMAGE_TAG"
```

### 14.4 Validate

Check:

- `/health`
- ticket list endpoint
- CSV import endpoint if affected
- Excel export if affected

## 15. Frontend-Only Update Procedure

Use this when only frontend code changes.

### 15.1 Rebuild Frontend

```sh
cd /Users/frankbogle/PycharmProjects/PLM_Tickets/frontend

VITE_API_BASE_URL="https://$BACKEND_FQDN" npm run build
```

### 15.2 Publish New `dist`

Deploy the new `frontend/dist` output to Azure Static Web Apps.

### 15.3 Validate

Check:

- page load
- ticket filtering
- ticket save
- CSV upload
- Excel export button

## 16. Full Release Procedure

Use this when backend and frontend both change.

1. build and push a new backend image tag
2. update the Container App
3. rebuild the frontend against the correct backend URL
4. redeploy the frontend static output
5. validate main user flows end to end

## 17. Backend-Only Update Procedure With SQLite Persistence

Use this when only backend code changes and the deployed database must be preserved.

1. Build and push a new backend image tag.
2. Update the Container App image.
3. Do not replace the Azure File Share or the deployed `plm_tickets.db` unless you are intentionally promoting data.
4. Validate that the mounted database is still being used.

Important:

- backend redeployments should not wipe the mounted SQLite data
- the data lives in the Azure File Share, not in the container image

## 18. Promoting New Local Data After Initial Deployment

If you continue to enrich tickets locally before fully switching to the cloud instance, use a controlled overwrite process.

Recommended approach:

1. Stop local editing.
2. Stop remote editing.
3. Back up the current Azure file share copy.
4. Upload the newer local `backend/plm_tickets.db`.
5. Restart the backend Container App.
6. Validate ticket counts and selected enriched records.

Do not casually overwrite the deployed database without confirming which copy is newer.

## 19. Practical Lessons To Carry Across From `rfp_rag_assistant`

1. Do not rely on Azure CLI default resource groups
2. Always use a new backend image tag for redeployments
3. Be explicit about CORS origins
4. Treat deployment data separately from application code
5. Validate the real production URLs, not just local assumptions

## 20. Recommended Next Engineering Work In This Repo

Before first real deployment, the highest-value code changes would be:

1. environment-driven backend settings
2. frontend `VITE_API_BASE_URL`
3. backend Dockerfile
4. explicit deployment config for database persistence
5. a simple migration/backup script for SQLite data promotion
6. optional PostgreSQL migration path for later

## 21. Document Relationships

Related documents:

- [application_design.md](/Users/frankbogle/PycharmProjects/PLM_Tickets/docs/application_design.md:1)
- [deployment_and_data_migration.md](/Users/frankbogle/PycharmProjects/PLM_Tickets/docs/deployment_and_data_migration.md:1)
- [user_guide.md](/Users/frankbogle/PycharmProjects/PLM_Tickets/docs/user_guide.md:1)
