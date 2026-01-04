# Deploying ShopDongHo to Kubernetes (trial1)

This project is configured for deployment to a Kubernetes cluster, specifically targeting the `trial1` node.

## Prerequisites

- Docker installed locally.
- Access to a container registry (e.g., Docker Hub, GHCR).
- `kubectl` configured to your cluster.

## Deployment Steps

### 1. Build and Push the Docker Image

```bash
# Build the image
docker build -t <YOUR_REGISTRY>/shop-dongho:latest .

# Push to your registry
docker push <YOUR_REGISTRY>/shop-dongho:latest
```

### 2. Configure Secrets

Edit `k8s/secrets.yaml` and set a secure `django-secret-key`. Then apply it:

```bash
kubectl apply -f k8s/secrets.yaml
```

### 3. Deploy to Kubernetes

Apply the main deployment manifest:

```bash
kubectl apply -f k8s/deploy.yaml
```

### 4. Handling the Database (SQLite)

The deployment uses a PersistentVolumeClaim (`shop-dongho-data`) to store `db.sqlite3`.
To migrate your existing data:

1. Identify the pod: `kubectl get pods -n trial1`
2. Copy the file: `kubectl cp db.sqlite3 <POD_NAME>:/app/db.sqlite3 -n trial1`

## Domain Configuration

The ingress is configured for `dongho.hmz.one`. Ensure your DNS (likely Cloudflare per your setup) points to the public IP of the `trial1` node or your LoadBalancer.

- **Public IP (trial1):** `114.29.239.33`
- **Tailscale IP (trial1):** `100.85.164.40`
