# BÁO CÁO PHÂN TÍCH HỆ THỐNG SHOPDONGHO THEO MODULE & FLOW LOGIC

Hệ thống ShopDongHo là một ứng dụng website bán đồng hồ được triển khai trên nền tảng Kubernetes (K3s). Dưới đây là báo cáo phân tích theo module và luồng xử lý nghiệp vụ dành cho Business Analyst.[1]

## Module 1: Infrastructure & Deployment (Hạ Tầng)

### Mục đích nghiệp vụ
Module này đảm bảo hệ thống luôn sẵn sàng phục vụ khách hàng 24/7 với khả năng tự phục hồi khi gặp sự cố.[1]

### Các thành phần chính

| Thành phần | Vai trò nghiệp vụ | Thời gian xử lý |
|------------|------------------|-----------------|
| K3s Kubernetes | Tự động khởi động lại khi hệ thống lỗi | Tức thì |
| Traefik | Định tuyến request từ khách hàng đến ứng dụng | < 1 giây |
| Persistent Storage | Lưu trữ dữ liệu sản phẩm và đơn hàng | Vĩnh viễn |
| Docker Container | Đóng gói ứng dụng để dễ triển khai | N/A |

### Luồng triển khai (Deployment Flow)
```
BƯỚC 1: Cài đặt K3s (1 lần duy nhất)
   └─> Tạo môi trường Kubernetes trên server
   └─> Tự động cài Traefik và Storage
   
BƯỚC 2: Build ứng dụng từ source code
   └─> Clone code từ GitHub
   └─> Build Docker Image (~5 phút)
   └─> Xóa source code tạm
   
BƯỚC 3: Deploy lên Kubernetes
   └─> Tạo namespace và storage
   └─> Khởi chạy ứng dụng
   └─> Cấu hình routing domain
   
BƯỚC 4: Import dữ liệu
   └─> Copy database vào storage
   └─> Copy hình ảnh sản phẩm
   └─> Restart để áp dụng
```


## Module 2: Application Management (Quản Lý Ứng Dụng)

### Mục đích nghiệp vụ
Module này cho phép team vận hành cập nhật tính năng mới, sửa lỗi và giám sát hệ thống mà không làm gián đoạn dịch vụ.[2]

### Quy trình cập nhật code (Update Flow)

**Phương án 1: Cập nhật có thay đổi code (5 phút)**
```
Developer push code mới lên GitHub
   ↓
Sync code từ local về server (~1 phút)
   ↓
Build Docker image mới (~3 phút)
   ↓
Restart deployment (tự động)
   ↓
Theo dõi logs để verify
   ↓
Dọn dẹp source code tạm
```


**Phương án 2: Quick Restart (30 giây)**
- Dùng khi chỉ cần khởi động lại mà không đổi code
- Ứng dụng với restart ứng dụng bị lỗi tạm thời[2]

### Monitoring & Troubleshooting (Giám Sát)

**Các hoạt động kiểm tra thường xuyên:**
- Xem trạng thái pods (10 giây): Kiểm tra ứng dụng có đang chạy không
- Xem logs real-time: Phát hiện lỗi ngay khi xảy ra
- Test connectivity: Đảm bảo khách hàng truy cập được website[2]

## Module 3: Database Management (Quản Lý Cơ Sở Dữ Liệu)

### Mục đích nghiệp vụ
Quản lý dữ liệu sản phẩm, đơn hàng, khách hàng và đảm bảo không mất dữ liệu khi có sự cố.[2]

### Luồng backup định kỳ (Backup Flow)

```
BACKUP HÀNG NGÀY (2 phút):
   1. Tìm đường dẫn lưu trữ database
   2. Copy database với timestamp
   3. Backup hình ảnh sản phẩm
   4. Kiểm tra file backup thành công
```


### Luồng khôi phục dữ liệu (Restore Flow)

```
KHI CẦN KHÔI PHỤC (3 phút):
   1. Dừng ứng dụng (stop pods)
   2. Restore database từ bản backup
   3. Restore hình ảnh (nếu cần)
   4. Khởi động lại ứng dụng
   5. Verify dữ liệu đã được khôi phục
```


### Các thao tác Django Commands
- **Migrate database**: Cập nhật cấu trúc database khi có thay đổi
- **Create superuser**: Tạo tài khoản admin quản trị hệ thống
- **Collect static files**: Thu thập CSS/JS/Images để website hiển thị đúng[2]

## Module 4: Performance & Scaling (Hiệu Năng)

### Mục đích nghiệp vụ
Điều chỉnh tài nguyên hệ thống để đáp ứng lượng truy cập tăng giảm, tối ưu chi phí vận hành.[2]

### Scale Operations (Mở Rộng)

**Khi lượng truy cập tăng cao:**
```
Tăng số pods lên 3 
   └─> Kubernetes tự động phân phối traffic
   └─> Khả năng xử lý tăng gấp 3 lần
```

**Khi lượng truy cập bình thường:**
```
Giảm về 1 pod
   └─> Tiết kiệm tài nguyên server
   └─> Giảm chi phí vận hành
```


### Resource Monitoring
- CPU & Memory usage: Theo dõi tài nguyên đang sử dụng
- Disk usage: Đảm bảo đủ không gian lưu trữ cho dữ liệu và hình ảnh[2]

## Module 5: Debug & Emergency Response (Xử Lý Sự Cố)

### Mục đích nghiệp vụ
Phát hiện và khắc phục sự cố nhanh chóng để giảm thiểu thời gian ngừng dịch vụ, bảo vệ trải nghiệm khách hàng.[2]

### Các tình huống khẩn cấp

| Tình huống | Nguyên nhân | Cách xử lý | Thời gian |
|------------|-------------|-----------|-----------|
| Pod không start | Lỗi config hoặc image | Force delete pod, xem logs | 1-2 phút |
| App lỗi 500 | Lỗi code hoặc database | Xem logs, restart deployment | 1 phút |
| DNS không resolve | Cấu hình DNS sai | Restart Traefik | 30 giây |
| Website không truy cập | Network hoặc Ingress lỗi | Test connectivity từng layer | 2-3 phút |

[2]

### Luồng xử lý sự cố chuẩn

```
PHÁT HIỆN SỰ CỐ (Monitoring hoặc khách hàng báo)
   ↓
XEM LOGS để xác định nguyên nhân
   ↓
XEM EVENTS để hiểu context
   ↓
ÁP DỤNG GIẢI PHÁP tương ứng
   ↓
VERIFY hệ thống đã hoạt động
   ↓
GHI NHẬN incident để phòng tránh
```


## Module 6: Data Flow (Luồng Dữ Liệu End-to-End)

### Luồng request từ khách hàng

```
KHÁCH HÀNG truy cập dongho.hmz.one
   ↓
DNS resolve → IP 114.29.239.33
   ↓
TRAEFIK (Port 80) nhận request
   ↓
Route đến SERVICE (shop-dongho-svc)
   ↓
SERVICE forward đến POD (Django Container)
   ↓
DJANGO xử lý request:
   - Đọc database (SQLite)
   - Load hình ảnh từ storage
   - Render HTML
   ↓
Trả response về cho KHÁCH HÀNG
```


### Persistence Flow (Lưu Trữ Lâu Dài)

```
USER upload hình ảnh sản phẩm
   ↓
Django save vào /app/media (trong container)
   ↓
Kubernetes mount từ Persistent Volume
   ↓
File được lưu vào /var/lib/rancher/k3s/storage/...
   ↓
Dữ liệu tồn tại ngay cả khi container restart
```


## Module 7: Security & Maintenance (Bảo Mật & Bảo Trì)

### Environment Variables Security
- Django SECRET_KEY được lưu trong Kubernetes Secrets
- Không lưu mật khẩu trong source code
- Environment variables được inject vào container khi runtime[1]

### Maintenance Tasks (Bảo Trì Định Kỳ)

**Hàng ngày:**
- Kiểm tra logs để phát hiện lỗi
- Verify website hoạt động bình thường
- Backup database[2]

**Hàng tuần:**
- Xóa old Docker images để tiết kiệm disk
- Review resource usage
- Xóa old backups không cần thiết[2]

**Khi có update:**
- Test trên môi trường local trước
- Backup database trước khi deploy
- Deploy code mới theo quy trình chuẩn
- Verify sau khi deploy[1][2]

## Tổng Kết Các Module

### Dependencies (Phụ Thuộc)

```
Infrastructure (Module 1)
   ├─> Application Management (Module 2)
   ├─> Database Management (Module 3)
   ├─> Performance & Scaling (Module 4)
   └─> Debug & Emergency (Module 5)

Data Flow (Module 6) - Xuyên suốt tất cả modules

Security & Maintenance (Module 7) - Áp dụng cho tất cả modules
```

### Key Success Metrics (Chỉ Số Quan Trọng)

- **Uptime**: Hệ thống hoạt động 99.9% thời gian
- **Deployment time**: 5 phút để update code mới
- **Recovery time**: < 3 phút khi có sự cố
- **Backup frequency**: Hàng ngày, lưu 30 ngày
- **Response time**: < 1 giây cho request thông thường[1][2]

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/103957372/a90ccc71-9b85-4fd2-beec-29b552f0914d/DEPLOYMENT_GUIDE.md)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/103957372/51ffcc3a-e1e0-4c4b-9bdd-8c8ae51432d8/QUICK_COMMANDS.md)