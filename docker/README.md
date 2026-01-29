# NetBox GCP Inventory - Docker Deployment

This Docker setup allows you to quickly deploy the customized NetBox with GCP inventory management features.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/GoteamQ/netbox.git
cd netbox
git checkout feature/gcp-inventory
```

### 2. Start the Services

```bash
cd docker
docker compose up -d
```

### 3. Access NetBox

Open your browser and navigate to:
- **URL**: http://localhost:8000
- **Username**: admin
- **Password**: admin

## Services

| Service | Description | Port |
|---------|-------------|------|
| netbox | Main NetBox application | 8000 |
| netbox-worker | Background task worker | - |
| netbox-housekeeping | Scheduled maintenance tasks | - |
| postgres | PostgreSQL database | 5432 (internal) |
| redis | Redis for task queue | 6379 (internal) |
| redis-cache | Redis for caching | 6379 (internal) |

## Configuration

### Environment Variables

Edit `env/netbox.env` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| ALLOWED_HOSTS | * | Comma-separated list of allowed hostnames |
| DB_HOST | postgres | Database hostname |
| DB_NAME | netbox | Database name |
| DB_USER | netbox | Database username |
| DB_PASSWORD | netbox | Database password |
| REDIS_HOST | redis | Redis hostname |
| SECRET_KEY | (generated) | Django secret key |
| SUPERUSER_NAME | admin | Initial admin username |
| SUPERUSER_EMAIL | admin@example.com | Initial admin email |
| SUPERUSER_PASSWORD | admin | Initial admin password |
| DEBUG | False | Enable debug mode |

### Production Deployment

For production, update the following:

1. Generate a new `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

2. Set strong passwords for database and admin user

3. Configure `ALLOWED_HOSTS` with your domain

4. Consider using HTTPS with a reverse proxy (nginx/traefik)

## GCP Discovery Setup

### 1. Create a GCP Service Account

1. Go to GCP Console → IAM & Admin → Service Accounts
2. Create a new service account
3. Grant the following roles:
   - `roles/viewer`
   - `roles/resourcemanager.organizationViewer`
   - `roles/compute.viewer`
   - `roles/container.viewer`
   - `roles/cloudsql.viewer`
   - `roles/storage.objectViewer`
4. Create and download a JSON key

### 2. Add Organization in NetBox

1. Navigate to **Google Cloud → Organizations → GCP Organizations**
2. Click **+ Add**
3. Enter your organization details:
   - Name: Your organization display name
   - Organization ID: Your GCP organization ID (numeric)
   - Service Account JSON: Paste the entire JSON key content
4. Select which resources to discover
5. Save

### 3. Trigger Discovery

**Via UI:**
- Go to the organization detail page
- Click the "Discover" button

**Via API:**
```bash
curl -X POST http://localhost:8000/api/gcp/organizations/1/discover/ \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json"
```

## Commands

### View Logs
```bash
docker compose logs -f netbox
```

### Restart Services
```bash
docker compose restart
```

### Stop Services
```bash
docker compose down
```

### Remove All Data
```bash
docker compose down -v
```

### Rebuild After Code Changes
```bash
docker compose build --no-cache
docker compose up -d
```

## Troubleshooting

### Database Connection Issues
```bash
docker compose logs postgres
```

### NetBox Startup Issues
```bash
docker compose logs netbox
```

### Run Django Management Commands
```bash
docker compose exec netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py shell
```

## GCP Menu Structure

The left navigation panel includes:

- **Organizations** - GCP Organizations, Discovery Logs
- **Projects** - GCP Projects
- **Compute** - Instances, Templates, Groups
- **Networking** - VPCs, Subnets, Firewalls, Routers, NAT, Load Balancers
- **Network Connectivity** - NCC Hubs, NCC Spokes, Interconnect Attachments
- **Hybrid Connectivity** - VPN Gateways, External VPN Gateways, VPN Tunnels
- **Databases** - Cloud SQL, Spanner, Firestore, Bigtable, Memorystore
- **Storage** - Buckets, Persistent Disks
- **Kubernetes** - GKE Clusters, Node Pools
- **Serverless** - Cloud Functions, Cloud Run
- **Messaging** - Pub/Sub Topics, Subscriptions
- **Security** - Secret Manager
- **DNS** - DNS Zones, DNS Records
- **IAM** - Service Accounts, Roles, Bindings
