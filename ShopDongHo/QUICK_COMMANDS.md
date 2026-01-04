# Lệnh Quản Lý Nhanh ShopDongHo trên K8s

## 🚀 SSH vào Server

### PuTTY (Windows):

```cmd
"C:\Program Files\PuTTY\putty.exe" root@114.29.239.33 -pw thachanh
```

### SSH thông thường:

```bash
ssh root@114.29.239.33
# Password: thachanh
```

---

## 📊 Kiểm Tra Trạng Thái (10 giây)

```bash
# Xem tất cả resources
kubectl get all -n trial1

# Xem logs app (real-time)
kubectl logs -n trial1 -l app=shop-dongho -f

# Xem pods
kubectl get pods -n trial1

# Kiểm tra ingress
kubectl get ingress -n trial1

# Test app từ server
curl -I http://dongho.hmz.one
```

---

## 🔄 Update Code (5 phút)

### Cách 1: Build Image Mới (Khuyên dùng)

```bash
# 1. Sync code mới từ local
# (Chạy từ máy local, không phải trial1)
scp -r "e:\Pet Projects\Viebal\VPS\k8s\ShopDongHo" root@trial1:/tmp/ShopDongHo

# 2. SSH vào trial1
ssh root@trial1

# 3. Build image mới
cd /tmp/ShopDongHo
docker build --network=host -t shop-dongho:latest .

# 4. Restart pods
kubectl rollout restart deployment/shop-dongho -n trial1

# 5. Theo dõi deployment
kubectl rollout status deployment/shop-dongho -n trial1

# 6. Xem logs
kubectl logs -n trial1 -l app=shop-dongho -f

# 7. Dọn dẹp source code
rm -rf /tmp/ShopDongHo
```

### Cách 2: Quick Restart (Không thay đổi code)

```bash
kubectl rollout restart deployment/shop-dongho -n trial1
kubectl rollout status deployment/shop-dongho -n trial1
```

---

## 🗄️ Database Management

### Exec vào Pod

```bash
# Mở shell trong pod
kubectl exec -it -n trial1 deployment/shop-dongho -- bash

# Sau khi vào pod:
python manage.py migrate               # Chạy DB migrations
python manage.py createsuperuser       # Tạo admin user
python manage.py shell                 # Django shell
exit                                   # Thoát
```

### Chạy Django Commands (Không vào pod)

```bash
# Migrate database
kubectl exec -n trial1 deployment/shop-dongho -- python manage.py migrate

# Tạo superuser (interactive)
kubectl exec -it -n trial1 deployment/shop-dongho -- python manage.py createsuperuser

# Collect static files
kubectl exec -n trial1 deployment/shop-dongho -- python manage.py collectstatic --noinput
```

---

## 💾 Backup Database (2 phút)

```bash
# Tìm PVC path
PVC_ID=$(kubectl get pvc -n trial1 shop-dongho-data -o jsonpath='{.spec.volumeName}')
STORAGE_PATH="/var/lib/rancher/k3s/storage/${PVC_ID}_trial1_shop-dongho-data"

# Tạo thư mục backup
mkdir -p /root/backups

# Backup database với timestamp
cp ${STORAGE_PATH}/data/db.sqlite3 /root/backups/db.sqlite3.$(date +%Y%m%d_%H%M%S)

# Backup media files
tar -czf /root/backups/media_$(date +%Y%m%d_%H%M%S).tar.gz -C ${STORAGE_PATH} media/

# Xem backups
ls -lh /root/backups/
```

---

## 🔙 Restore Database (3 phút)

```bash
# 1. Stop pods
kubectl scale deployment shop-dongho -n trial1 --replicas=0

# 2. Restore database (thay YYYYMMDD_HHMMSS bằng backup thực tế)
PVC_ID=$(kubectl get pvc -n trial1 shop-dongho-data -o jsonpath='{.spec.volumeName}')
STORAGE_PATH="/var/lib/rancher/k3s/storage/${PVC_ID}_trial1_shop-dongho-data"
cp /root/backups/db.sqlite3.YYYYMMDD_HHMMSS ${STORAGE_PATH}/data/db.sqlite3

# 3. Restore media (optional)
tar -xzf /root/backups/media_YYYYMMDD_HHMMSS.tar.gz -C ${STORAGE_PATH}

# 4. Start pods
kubectl scale deployment shop-dongho -n trial1 --replicas=1

# 5. Verify
kubectl get pods -n trial1
```

---

## 🐛 Debug & Troubleshoot

### Xem Logs

```bash
# Logs hiện tại
kubectl logs -n trial1 -l app=shop-dongho

# Logs real-time (Ctrl+C để thoát)
kubectl logs -n trial1 -l app=shop-dongho -f

# Logs của pod trước đó (nếu pod bị crash)
kubectl logs -n trial1 -l app=shop-dongho --previous

# Xem init container logs
POD_NAME=$(kubectl get pod -n trial1 -l app=shop-dongho -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n trial1 $POD_NAME -c init-dirs
```

### Xem Events

```bash
# Events của namespace
kubectl get events -n trial1 --sort-by='.lastTimestamp'

# Chi tiết pod
kubectl describe pod -n trial1 -l app=shop-dongho
```

### Port Forward (Test từ local)

```bash
# Forward port để test từ máy local
kubectl port-forward -n trial1 svc/shop-dongho-svc 8000:80

# Mở browser: http://localhost:8000
# Ctrl+C để stop
```

### Kiểm Tra Environment Variables

```bash
kubectl exec -n trial1 deployment/shop-dongho -- env | grep DJANGO
```

### Test Connectivity

```bash
# Test từ trong cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl -I http://shop-dongho-svc.trial1.svc.cluster.local

# Test từ trial1 server
curl -H 'Host: dongho.hmz.one' http://localhost

# Test từ internet
curl -I http://dongho.hmz.one
```

---

## ⚙️ Scale & Performance

### Scale Pods

```bash
# Tăng số pods lên 3
kubectl scale deployment shop-dongho -n trial1 --replicas=3

# Giảm về 1 pod
kubectl scale deployment shop-dongho -n trial1 --replicas=1

# Xem trạng thái
kubectl get pods -n trial1
```

### Resource Usage

```bash
# CPU & Memory usage
kubectl top pods -n trial1
kubectl top nodes

# Disk usage trong pod
kubectl exec -n trial1 deployment/shop-dongho -- df -h /app/data /app/media
```

---

## 🧹 Dọn Dẹp

### Xóa Old Docker Images

```bash
# Xem images
docker images | grep shop-dongho

# Xóa images unused
docker image prune -a

# Xóa specific image
docker rmi shop-dongho:old-tag
```

### Xóa Old ReplicaSets

```bash
# Xem replicasets
kubectl get rs -n trial1

# K8s tự động giữ 10 revisions, nhưng có thể xóa manual:
kubectl delete rs -n trial1 shop-dongho-56cf774bf6  # Thay bằng tên thực tế
```

### Restart K3s (Nếu cần)

```bash
# Restart K3s service
systemctl restart k3s

# Xem status
systemctl status k3s

# Xem nodes
kubectl get nodes
```

---

## 🚨 Emergency Commands

### Pod Không Start

```bash
# Force delete pod
kubectl delete pod -n trial1 -l app=shop-dongho --force --grace-period=0

# Xem tại sao không start
kubectl describe pod -n trial1 -l app=shop-dongho
```

### App Bị Lỗi 500

```bash
# Xem logs để tìm error
kubectl logs -n trial1 -l app=shop-dongho | tail -100

# Restart deployment
kubectl rollout restart deployment/shop-dongho -n trial1
```

### DNS Không Resolve

```bash
# Kiểm tra từ trial1
nslookup dongho.hmz.one

# Restart Traefik
kubectl rollout restart deployment/traefik -n kube-system
```

### Xóa Hoàn Toàn & Deploy Lại

```bash
# !!! CẨNTHẬN: Xóa hết data !!!

# 1. Xóa tất cả
kubectl delete namespace trial1

# 2. Deploy lại
kubectl apply -f /path/to/secrets.yaml
kubectl apply -f /path/to/deploy_final.yaml

# 3. Copy data vào PVC mới
# (Follow DEPLOYMENT_GUIDE.md - Bước 6)
```

---

## 📞 Quick Reference

| Mục đích     | Lệnh                                                          |
| ------------ | ------------------------------------------------------------- |
| Xem pods     | `kubectl get pods -n trial1`                                  |
| Xem logs     | `kubectl logs -n trial1 -l app=shop-dongho -f`                |
| Restart      | `kubectl rollout restart deployment/shop-dongho -n trial1`    |
| Exec vào pod | `kubectl exec -it -n trial1 deployment/shop-dongho -- bash`   |
| Xem events   | `kubectl get events -n trial1`                                |
| Test app     | `curl -I http://dongho.hmz.one`                               |
| Backup DB    | `cp ${STORAGE_PATH}/data/db.sqlite3 /root/backups/`           |
| Scale        | `kubectl scale deployment shop-dongho -n trial1 --replicas=N` |

---

## 🔗 Links

- **App URL**: http://dongho.hmz.one
- **Admin**: http://dongho.hmz.one/admincustom/
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **K8s Manifests**: `k8s/deploy_final.yaml`

---

**Ghi chú**:

- Tất cả lệnh trên chạy trên server **trial1** (trừ khi có ghi chú khác)
- Thay `YYYYMMDD_HHMMSS` bằng timestamp thực tế khi restore
- Luôn backup trước khi thay đổi quan trọng!
