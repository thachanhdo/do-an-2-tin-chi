# Hướng Dẫn Deploy ShopDongHo lên Kubernetes

## 📋 Tổng Quan

Dự án này deploy ứng dụng Django **ShopDongHo** (Website bán đồng hồ) lên Kubernetes cluster trên server `trial1` sử dụng domain `dongho.hmz.one`.

### Giải Thích Công Nghệ

#### **Kubernetes (K8s) là gì?**

**Kubernetes** là một nền tảng mã nguồn mở để quản lý, triển khai và tự động hóa các ứng dụng container. Nó giúp:

- **Tự động triển khai** (automatic deployment)
- **Tự động mở rộng** (auto-scaling)
- **Tự phục hồi** (self-healing khi container bị lỗi)
- **Cân bằng tải** (load balancing)
- **Quản lý storage** (persistent volumes)

**Ví dụ**: Nếu server của bạn bị sập hoặc ứng dụng bị lỗi, Kubernetes tự động restart và đảm bảo ứng dụng luôn chạy.

#### **K3s là gì?**

**K3s** là một phiên bản **lightweight (nhẹ)** của Kubernetes được thiết kế cho:

- **IoT devices** (thiết bị nhỏ)
- **Edge computing** (máy chủ nhỏ)
- **Single-node clusters** (chỉ 1 server)

**So sánh**:

- **Kubernetes gốc**: ~500MB binary, phức tạp, cần nhiều tài nguyên
- **K3s**: ~70MB binary, đơn giản, chạy ngay trên 1 server nhỏ

**Vai trò trong dự án này**:

- K3s tạo một Kubernetes cluster trên server `trial1`
- K3s **tự động cài sẵn**:
  - ✅ Traefik (Ingress Controller) → Route HTTP traffic
  - ✅ Local-path storage → Lưu database & media files
  - ✅ CoreDNS → DNS cho cluster
  - ✅ Metrics server → Monitoring resources
- Chúng ta chỉ cần **1 lệnh cài đặt** là có ngay Kubernetes cluster hoàn chỉnh!

#### **Kiến Trúc Hệ Thống**

```
┌─────────────────────────────────────────────┐
│  Internet                                   │
│  User truy cập: http://dongho.hmz.one       │
└──────────────────┬──────────────────────────┘
                   │ DNS: dongho.hmz.one
                   │ → 114.29.239.33
                   ▼
┌─────────────────────────────────────────────┐
│  Server trial1 (114.29.239.33)              │
│                                              │
│  ┌──Kubernetes (K3s)─────────────────────┐  │
│  │                                        │  │
│  │  1️⃣ TRAEFIK (Port 80)                  │  │
│  │     ↓ Route based on domain           │  │
│  │     dongho.hmz.one → shop-dongho-svc  │  │
│  │                                        │  │
│  │  2️⃣ SERVICE (ClusterIP)                │  │
│  │     shop-dongho-svc:80                │  │
│  │     ↓ Forward to pod                  │  │
│  │                                        │  │
│  │  3️⃣ POD (Container)                    │  │
│  │     ┌──────────────────────────┐       │  │
│  │     │ Django + Gunicorn:8000   │       │  │
│  │     │ - Python 3.11            │       │  │
│  │     │ - 3 workers              │       │  │
│  │     │                          │       │  │
│  │     │ Volumes:                 │       │  │
│  │     │ /app/data ← PVC (DB)     │       │  │
│  │     │ /app/media ← PVC (Images)│       │  │
│  │     └──────────────────────────┘       │  │
│  │                ↓                       │  │
│  │  4️⃣ PERSISTENT VOLUME (Local-path)     │  │
│  │     /var/lib/rancher/k3s/storage/...  │  │
│  │     ├── data/db.sqlite3 (Database)    │  │
│  │     └── media/uploads/*.webp (Images) │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘

Luồng request:
1. User → dongho.hmz.one
2. DNS → 114.29.239.33 (trial1)
3. Traefik (port 80) nhận request
4. Traefik route → shop-dongho-svc
5. Service forward → Pod (container)
6. Django/Gunicorn xử lý request
7. Trả về HTML/CSS/Images cho user
```

---

## 🚀 Các Bước Deploy

### Bước 1: Cài Đặt K3s trên trial1

```bash
# SSH vào server
ssh root@trial1

# Cài K3s với Docker runtime (1 lẹnh duy nhất!)
curl -sfL https://get.k3s.io | sh -s - --docker

# Kiểm tra
kubectl get nodes
# Output: trial1   Ready    control-plane   <time>   v1.34.3+k3s1
```

**Sau lệnh này, bạn đã có**:

- ✅ Kubernetes cluster hoạt động
- ✅ Traefik Ingress Controller (tự động)
- ✅ Storage provisioner (tự động)
- ✅ kubectl command để quản lý

---

### Bước 2: Clone Source Code từ GitHub

```bash
# Trên server trial1
cd /tmp
git clone https://github.com/thachanhdo/do-an-2-tin-chi.git ShopDongHo
cd ShopDongHo/ShopDongHo
```

**Tại sao dùng /tmp?**

- Source code chỉ cần để build Docker image
- Sau khi build xong, ta sẽ **xóa source code** để giữ server sạch
- Chỉ giữ lại Docker image và K8s resources

---

### Bước 3: Build Docker Image

```bash
# Build image từ Dockerfile
docker build --network=host -t shop-dongho:latest .
```

**Quá trình build**:

1. Tải Python 3.11 base image (~150MB)
2. Cài đặt system packages (gcc, libpq-dev)
3. Copy requirements.txt và cài Python packages
4. Copy toàn bộ code Django vào /app
5. Chạy `collectstatic` → Thu thập 1144 static files
6. Tạo image final (~549MB)

**Tại sao cần `--network=host`?**

- Cho Docker sử dụng network của host (trial1)
- Tránh lỗi DNS khi cài packages từ PyPI

---

### Bước 4: Apply Kubernetes Resources

```bash
# Apply secrets (Django SECRET_KEY)
kubectl apply -f /tmp/ShopDongHo/ShopDongHo/k8s/secrets.yaml

# Apply deployment (Namespace, PVC, Deployment, Service, Ingress)
kubectl apply -f /tmp/ShopDongHo/ShopDongHo/k8s/deploy_final.yaml
```

**Kubernetes tự động thực hiện**:

1. Tạo namespace `trial1`
2. Tạo PersistentVolumeClaim (1Gi storage)
3. K3s local-path provisioner tự động tạo folder: `/var/lib/rancher/k3s/storage/pvc-xxx`
4. Schedule pod lên node trial1
5. Chạy init container → Tạo `/app/data` và `/app/media`
6. Mount PVC vào pod
7. Start container Django với Gunicorn
8. Tạo ClusterIP Service (shop-dongho-svc)
9. Traefik tự động đọc Ingress config và route traffic

---

### Bước 5: Copy Database & Media Files vào PVC

```bash
# Tìm PVC storage path
PVC_ID=$(kubectl get pvc -n trial1 shop-dongho-data -o jsonpath='{.spec.volumeName}')
STORAGE_PATH="/var/lib/rancher/k3s/storage/${PVC_ID}_trial1_shop-dongho-data"

# Upload database từ local
scp "e:\Pet Projects\Viebal\VPS\k8s\ShopDongHo\db.sqlite3" root@trial1:/tmp/

# Copy vào PVC
mkdir -p ${STORAGE_PATH}/data
cp /tmp/db.sqlite3 ${STORAGE_PATH}/data/

# Upload media files từ local
scp -r "e:\Pet Projects\Viebal\VPS\k8s\ShopDongHo\media" root@trial1:/tmp/

# Copy vào PVC
cp -r /tmp/media/uploads ${STORAGE_PATH}/media/

# Set permissions
chown -R 1000:1000 ${STORAGE_PATH}
```

---

### Bước 6: Restart Pod để Apply Changes

```bash
# Xóa pod, K8s tự động tạo pod mới
kubectl delete pod -n trial1 -l app=shop-dongho

# Hoặc restart deployment
kubectl rollout restart deployment/shop-dongho -n trial1

# Kiểm tra
kubectl get pods -n trial1
# Output: shop-dongho-xxx   1/1   Running   0   10s
```

---

### Bước 7: Cấu Hình DNS

Trỏ domain `dongho.hmz.one` về IP của trial1:

**DNS Record**:

```
Type: A
Name: dongho
Value: 114.29.239.33
TTL: 300
```

---

### Bước 8: Dọn Dẹp Source Code

```bash
# Xóa source code tạm
rm -rf /tmp/ShopDongHo /tmp/db.sqlite3 /tmp/media

# Verify server sạch sẽ
ls /tmp/
```

**Kết quả**:

- ✅ Source code đã bị xóa
- ✅ Docker image vẫn tồn tại: `shop-dongho:latest`
- ✅ K8s resources đang chạy
- ✅ Data trong PVC an toàn

---

### Bước 9: Verify Deployment

```bash
# Kiểm tra pods
kubectl get pods -n trial1
# Output: shop-dongho-xxx   1/1   Running   0   <time>

# Xem logs
kubectl logs -n trial1 -l app=shop-dongho

# Kiểm tra ingress
kubectl get ingress -n trial1
# Output: shop-dongho-ingress   traefik   dongho.hmz.one   114.29.239.33   80

# Test từ internet
curl -I http://dongho.hmz.one
# Output: HTTP/1.1 200 OK
```

---

## 📚 Kubernetes Resources Explained

### 1. Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: trial1
```

**Vai trò**: Tách biệt resources, giống như folder trong máy tính.

### 2. PersistentVolumeClaim (PVC)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shop-dongho-data
  namespace: trial1
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 1Gi
```

**Vai trò**: Yêu cầu 1Gi storage để lưu database và media files. K3s tự động tạo folder `/var/lib/rancher/k3s/storage/pvc-xxx` và mount vào pod.

### 3. Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-dongho
spec:
  replicas: 1
  template:
    spec:
      initContainers: [...] # Tạo folders
      containers:
        - name: shop-dongho
          image: shop-dongho:latest
          env:
            - name: DJANGO_SECRET_KEY
              valueFrom:
                secretKeyRef: ...
          volumeMounts:
            - name: storage
              mountPath: /app/data
              subPath: data
```

**Vai trò**: Định nghĩa cách chạy ứng dụng, bao gồm image, environment variables, volumes.

### 4. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: shop-dongho-svc
spec:
  selector:
    app: shop-dongho
  ports:
    - port: 80
      targetPort: 8000
```

**Vai trò**: Expose pod ra một ClusterIP cố định. Ingress sẽ route traffic đến Service này.

### 5. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop-dongho-ingress
spec:
  rules:
    - host: dongho.hmz.one
      http:
        paths:
          - path: /
            backend:
              service:
                name: shop-dongho-svc
                port:
                  number: 80
```

**Vai trò**: Cho Traefik biết: "Request đến `dongho.hmz.one` → Forward đến service `shop-dongho-svc`".

---

## 🔄 Update Code (Workflow Hoàn Chỉnh)

### Khi có thay đổi code:

```bash
# 1. Commit và push lên GitHub (từ máy local)
cd "e:\Pet Projects\Viebal\VPS\k8s\ShopDongHo"
git add -A
git commit -m "Update feature X"
git push

# 2. SSH vào trial1
ssh root@trial1

# 3. Clone code mới và build
cd /tmp
rm -rf ShopDongHo
git clone https://github.com/thachanhdo/do-an-2-tin-chi.git ShopDongHo
cd ShopDongHo/ShopDongHo
docker build --network=host -t shop-dongho:latest .

# 4. Restart deployment
kubectl rollout restart deployment/shop-dongho -n trial1

# 5. Theo dõi deployment
kubectl rollout status deployment/shop-dongho -n trial1

# 6. Xem logs
kubectl logs -n trial1 -l app=shop-dongho -f

# 7. Dọn dẹp
cd /tmp
rm -rf ShopDongHo

# 8. Verify
curl -I http://dongho.hmz.one
```

## 🔧 Quản Lý & Debug

### Xem Logs

```bash
# Real-time logs
kubectl logs -n trial1 -l app=shop-dongho -f

# Logs của pod trước (nếu pod bị crash)
kubectl logs -n trial1 -l app=shop-dongho --previous
```

### Exec vào Pod

```bash
# Mở shell trong pod
kubectl exec -it -n trial1 deployment/shop-dongho -- bash

# Trong pod, chạy Django commands:
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### Backup Database

```bash
PVC_ID=$(kubectl get pvc -n trial1 shop-dongho-data -o jsonpath='{.spec.volumeName}')
STORAGE_PATH="/var/lib/rancher/k3s/storage/${PVC_ID}_trial1_shop-dongho-data"

mkdir -p /root/backups
cp ${STORAGE_PATH}/data/db.sqlite3 \
   /root/backups/db.sqlite3.$(date +%Y%m%d_%H%M%S)
```

### Restore Database

```bash
# 1. Stop pods
kubectl scale deployment shop-dongho -n trial1 --replicas=0

# 2. Restore
cp /root/backups/db.sqlite3.20260104_140000 \
   ${STORAGE_PATH}/data/db.sqlite3

# 3. Start pods
kubectl scale deployment shop-dongho -n trial1 --replicas=1
```

---

## 🐛 Troubleshooting

### Pod không start

```bash
# Xem lỗi
kubectl describe pod -n trial1 -l app=shop-dongho
kubectl logs -n trial1 -l app=shop-dongho --previous

# Common issues:
# - Image pull error → Check if image exists: docker images
# - CrashLoopBackOff → Check logs
# - PVC không mount → Check PVC: kubectl get pvc -n trial1
```

### Website không truy cập được

```bash
# 1. Kiểm tra DNS
nslookup dongho.hmz.one
# Phải trả về: 114.29.239.33

# 2. Kiểm tra Traefik
kubectl get svc -n kube-system traefik
# EXTERNAL-IP phải là 114.29.239.33

# 3. Test từ trial1
curl -H 'Host: dongho.hmz.one' http://localhost

# 4. Kiểm tra ingress
kubectl describe ingress -n trial1 shop-dongho-ingress
```

## 📝 Tổng Kết

### Công Nghệ Sử Dụng

- **K3s**: Lightweight Kubernetes (v1.34.3)
- **Traefik**: Ingress Controller (tự động với K3s)
- **Local-path**: Storage provisioner (tự động với K3s)
- **Docker**: Container runtime
- **Django 5.0.4**: Web framework
- **Gunicorn**: WSGI server (3 workers)
- **WhiteNoise**: Static files serving
- **SQLite**: Database (persistent storage)

### Ưu Điểm

- ✅ **Đơn giản**: Chỉ 1 server, cài K3s bằng 1 lệnh
- ✅ **Tự động**: K8s tự restart khi pod crash
- ✅ **Persistent**: Data không mất khi pod restart
- ✅ **Production-ready**: Gunicorn, DEBUG=False
- ✅ **Clean**: Source code không lưu trên server

### Giới Hạn

- ⚠️ **Single-node**: Không có HA (High Availability)
- ⚠️ **SQLite**: Không phù hợp cho traffic cao
- ⚠️ **No SSL**: Chưa cấu hình HTTPS
- ⚠️ **Manual deployment**: Chưa có CI/CD

### Next Steps (Tùy Chọn)

1. **HTTPS**: Cài cert-manager + Let's Encrypt
2. **Database**: Migrate sang PostgreSQL
3. **Auto-deploy**: GitHub Actions
4. **Monitoring**: Prometheus + Grafana
5. **Backup automation**: Kubernetes CronJob

---

**Tác giả**: Đỗ Thạch Anh (MSSV: 23730063)
**Ngày tạo**: 04/01/2026
**Version**: 2.0 (Updated with GitHub workflow)
