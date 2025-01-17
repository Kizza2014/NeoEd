FROM python:3.10

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file yêu cầu và cài đặt dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn
COPY . .

# Cấu hình cổng và lệnh khởi chạy
EXPOSE 8000
CMD ["fastapi", "run", "main.py"]


