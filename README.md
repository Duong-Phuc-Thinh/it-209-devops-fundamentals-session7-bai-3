# Bài Tập 3: Thiết lập Cơ sở dữ liệu và Tự cấu hình dịch vụ Systemd cho Spring Boot

Thư mục này chứa cấu hình dịch vụ Systemd và script Python tự động thiết lập môi trường để quản lý ứng dụng Spring Boot chạy ở cổng `8082`.

## Chức Năng Đã Thực Hiện
1. **Khởi tạo Database & Phân quyền MySQL**:
   - Database: `springboot_db`
   - User: `spring-admin` / Mật khẩu: `SpringSecure@123` được cấp toàn quyền (ALL PRIVILEGES) trên `springboot_db`.
2. **Tạo tài khoản hệ thống bảo mật**:
   - Tạo user hệ thống `spring-runner` không có quyền shell login (`/bin/false`) để chạy ứng dụng Spring Boot.
3. **Cấu hình Dịch vụ Systemd** (`spring-app.service`):
   - Khởi chạy dưới user `spring-runner`.
   - Lệnh thực thi: `/usr/bin/java -jar /opt/spring-app/app.jar --server.port=8082`.
   - Cơ chế tự động restart sau `10` giây nếu xảy ra crash đột ngột (`Restart=on-failure` và `RestartSec=10`).

---

## Hướng Dẫn Chạy Chương Trình

### Bước 1: Chuẩn bị tệp JAR ứng dụng
Đảm bảo tệp `app.jar` đã được đưa vào đúng thư mục làm việc:
```bash
sudo mkdir -p /opt/spring-app
sudo cp path/to/your/app.jar /opt/spring-app/app.jar
```

### Bước 2: Chạy Script Tự Động Thiết Lập
Chạy file `setup.py` dưới quyền `root` để tự động khởi tạo MySQL user, tạo system user, ghi file cấu hình systemd và nạp lại daemon:
```bash
sudo python3 setup.py
```

### Bước 3: Cấp quyền cho file JAR và khởi động dịch vụ
Cấp quyền sở hữu thư mục ứng dụng cho user `spring-runner` và khởi động dịch vụ:
```bash
sudo chown -R spring-runner:spring-runner /opt/spring-app
sudo systemctl start spring-app
```

---

## Hướng Dẫn Kiểm Tra Kết Quả

1. **Kiểm tra trạng thái dịch vụ**:
```bash
sudo systemctl status spring-app.service
```
*Kết quả mong đợi*: Dòng trạng thái hiển thị `Active: active (running)` và chạy dưới tiến trình của user `spring-runner`.

2. **Kiểm tra cổng lắng nghe**:
```bash
ss -tlnp | grep 8082
```
*Kết quả mong đợi*: Cổng `8082` đang được lắng nghe bởi tiến trình `java`.