FROM node:12.22.9

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép package.json và cài đặt dependencies
COPY package.json ./
RUN npm install

# Sao chép mã nguồn
COPY . .

# Build ứng dụng nếu cần
RUN npm run build

# Cấu hình cổng và lệnh khởi chạy
EXPOSE 3000
CMD ["npm", "start"]
