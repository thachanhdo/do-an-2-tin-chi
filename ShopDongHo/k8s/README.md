# ShopDongHo - Kubernetes Deployment

Website bán đồng hồ được deploy lên Kubernetes cluster trên server `trial1`.

## 🌐 Thông Tin

- **URL Production**: http://dongho.hmz.one
- **Server**: trial1 (114.29.239.33)
- **Kubernetes**: K3s v1.34.3
- **Framework**: Django 5.0.4 + Gunicorn
- **Database**: SQLite (Persistent Storage)
- **Status**: ✅ Running (Images loading successfully)

## 🚀 GitHub Repository

```
https://github.com/thachanhdo/do-an-2-tin-chi.git
```

## 📚 Tài Liệu Đầy Đủ

1. **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Hướng dẫn deploy chi tiết từ đầu đến cuối

   - Giải thích Kubernetes & K3s là gì
   - Kiến trúc hệ thống
   - 9 bước deployment hoàn chỉnh
   - Clone từ GitHub (không cần copy từ local)
   - Troubleshooting guide

2. **[QUICK_COMMANDS.md](./QUICK_COMMANDS.md)** - Các lệnh quản lý nhanh hàng ngày

   - Kiểm tra trạng thái (10 giây)
   - Update code từ GitHub (5 phút)
   - Backup database (2 phút)
   - Restore database (3 phút)
   - Debug commands
   - Emergency procedures

3. **[DEPLOYMENT_COMPLETE.md](./DEPLOYMENT_COMPLETE.md)** - Tổng kết deployment

## 🔄 Quick Start - Update Code

### Clone từ GitHub và Deploy:

```bash
# 1. SSH vào server
ssh root@trial1

# 2. Clone code mới từ GitHub
cd /tmp
rm -rf ShopDongHo
git clone https://github.com/thachanhdo/do-an-2-tin-chi.git ShopDongHo
cd ShopDongHo/ShopDongHo

# 3. Build Docker image
docker build --network=host -t shop-dongho:latest .

# 4. Restart deployment
kubectl rollout restart deployment/shop-dongho -n trial1

# 5. Theo dõi deployment
kubectl rollout status deployment/shop-dongho -n trial1

# 6. Dọn dẹp source code
cd /tmp
rm -rf ShopDongHo

# 7. Verify
kubectl get pods -n trial1
curl -I http://dongho.hmz.one
```

## 📊 Kiểm Tra Nhanh

```bash
# Xem pods
ssh root@trial1 "kubectl get pods -n trial1"

# Xem logs
ssh root@trial1 "kubectl logs -n trial1 -l app=shop-dongho -f"

# Test app
curl -I http://dongho.hmz.one
curl -I http://dongho.hmz.one/media/uploads/anh1.webp  # Test images
```

## 💾 Backup Database

```bash
ssh root@trial1
PVC_ID=$(kubectl get pvc -n trial1 shop-dongho-data -o jsonpath='{.spec.volumeName}')
mkdir -p /root/backups
cp /var/lib/rancher/k3s/storage/${PVC_ID}_trial1_shop-dongho-data/data/db.sqlite3 \
   /root/backups/db.sqlite3.$(date +%Y%m%d_%H%M%S)
```

## 🔑 Kubernetes Resources

- **Namespace**: `trial1`
- **Deployment**: `shop-dongho` (1 replica, Running)
- **Service**: `shop-dongho-svc` (ClusterIP, port 80)
- **Ingress**: `shop-dongho-ingress` (dongho.hmz.one)
- **PVC**: `shop-dongho-data` (1Gi, local-path, Bound)
- **Secret**: `shop-secrets` (django-secret-key)

## 🛠️ Stack Công Nghệ

### Infrastructure

- **K3s**: Lightweight Kubernetes (v1.34.3+k3s1)
- **Traefik**: Ingress Controller (tự động với K3s)
- **Local-path**: Storage provisioner (tự động với K3s)
- **Docker**: Container runtime (28.2.2)

### Application

- **Django**: 5.0.4 (Web framework)
- **Gunicorn**: 23.0.0 (WSGI server, 3 workers)
- **WhiteNoise**: Static files serving
- **Custom Middleware**: Media files serving trong production
- **SQLite**: Database (persistent via PVC)
- **Pillow**: Image processing

## ✅ Tính Năng Đã Triển Khai

- ✅ **Auto-deployment**: Clone từ GitHub, build, deploy
- ✅ **Persistent Storage**: Database & media files không mất khi restart
- ✅ **Static Files**: WhiteNoise serve CSS/JS
- ✅ **Media Files**: Custom middleware serve images từ PVC
- ✅ **Production Config**: DEBUG=False, ALLOWED_HOSTS configured
- ✅ **Secrets Management**: Django SECRET_KEY trong Kubernetes Secret
- ✅ **Clean Server**: Source code tự động dọn sau mỗi build

## 📁 Cấu Trúc Thư Mục K8s

```
k8s/
├── deploy_final.yaml      # Main deployment manifest (Namespace, PVC, Deployment, Service, Ingress)
├── secrets.yaml           # Kubernetes secrets (Django SECRET_KEY)
├── deploy_test.yaml       # Test deployment (archived)
├── ingress_test.yaml      # Test ingress (archived)
└── README.md              # This file
```

## 🔒 Security

- Django `SECRET_KEY` stored in Kubernetes Secret
- `DEBUG = False` in production
- `ALLOWED_HOSTS` restricted to `dongho.hmz.one`
- `CSRF_TRUSTED_ORIGINS` configured
- No source code on production server
- SQLite database in PVC (not in container)

## 👥 Sinh viên thực hiện

- **Đỗ Thạch Anh** - MSSV: 23730063

## 📝 Ghi chú

- ✅ Source code được quản lý trên GitHub (không còn trên server)
- ✅ Mọi thay đổi code cần push lên GitHub trước khi deploy
- ✅ Database và media files được lưu persistent qua PVC
- ✅ Custom middleware cho phép Gunicorn serve media files
- ✅ Build process tự động: `git clone` → `docker build` → `kubectl rollout restart`
- 📘 Xem `DEPLOYMENT_GUIDE.md` để hiểu chi tiết Kubernetes & K3s
- ⚡ Xem `QUICK_COMMANDS.md` để có danh sách lệnh quản lý

## 🔗 Links

- **Website**: http://dongho.hmz.one
- **GitHub**: https://github.com/thachanhdo/do-an-2-tin-chi
- **Admin Panel**: http://dongho.hmz.one/admincustom/
