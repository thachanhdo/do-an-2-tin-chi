# ShopDongHo - Kubernetes Deployment

Website bán đồng hồ được deploy lên Kubernetes cluster trên server `trial1`.

## 🌐 Thông Tin

- **URL Production**: http://dongho.hmz.one
- **Server**: trial1 (114.29.239.33)
- **Kubernetes**: K3s v1.34.3
- **Framework**: Django 5.0.4 + Gunicorn
- **Database**: SQLite (Persistent Storage)

## 📚 Tài Liệu

1. **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Hướng dẫn deploy chi tiết từ đầu đến cuối
2. **[QUICK_COMMANDS.md](./QUICK_COMMANDS.md)** - Các lệnh quản lý nhanh hàng ngày
3. **[README_K8S.md](./README_K8S.md)** - Thông tin về K8s deployment

## 🚀 Quick Start

### Kiểm tra app đang chạy:

```bash
ssh root@trial1
kubectl get pods -n trial1
kubectl logs -n trial1 -l app=shop-dongho -f
```

### Update code mới:

```bash
# Từ máy local
scp -r "e:\Pet Projects\Viebal\VPS\k8s\ShopDongHo" root@trial1:/tmp/ShopDongHo

# Trên trial1
ssh root@trial1
cd /tmp/ShopDongHo
docker build --network=host -t shop-dongho:latest .
kubectl rollout restart deployment/shop-dongho -n trial1
rm -rf /tmp/ShopDongHo
```

### Backup database:

```bash
ssh root@trial1
PVC_ID=$(kubectl get pvc -n trial1 shop-dongho-data -o jsonpath='{.spec.volumeName}')
mkdir -p /root/backups
cp /var/lib/rancher/k3s/storage/${PVC_ID}_trial1_shop-dongho-data/data/db.sqlite3 \
   /root/backups/db.sqlite3.$(date +%Y%m%d_%H%M%S)
```

## 📁 Cấu Trúc

```
k8s/
├── deploy_final.yaml      # Kubernetes manifest chính (Namespace, PVC, Deployment, Service, Ingress)
├── secrets.yaml           # Kubernetes secrets (Django SECRET_KEY)
├── deploy_test.yaml       # Test deployment (không dùng)
└── ingress_test.yaml      # Test ingress (không dùng)
```

## 🔑 Kubernetes Resources

- **Namespace**: `trial1`
- **Deployment**: `shop-dongho` (1 replica)
- **Service**: `shop-dongho-svc` (ClusterIP, port 80)
- **Ingress**: `shop-dongho-ingress` (dongho.hmz.one)
- **PVC**: `shop-dongho-data` (1Gi, local-path)
- **Secret**: `shop-secrets` (django-secret-key)

## 👥 Sinh viên thực hiện

- **Đỗ Thạch Anh** - MSSV: 23730063

## 📝 Ghi chú

- Source code trên server trial1 đã được dọn sạch, chỉ giữ K8s resources
- Database và media files được lưu persistent qua PVC
- Mọi thay đổi code cần rebuild Docker image và restart deployment
- Xem `DEPLOYMENT_GUIDE.md` để hiểu chi tiết cách hệ thống hoạt động
- Xem `QUICK_COMMANDS.md` để có danh sách lệnh quản lý hàng ngày
