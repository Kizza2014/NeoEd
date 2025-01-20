// RegisterForm.js
import React, { useState } from "react";
import './Register.css';
import { useNavigate } from "react-router-dom";


function RegisterForm() {
  const [formData, setFormData] = useState({
    username: "",
    fullname: "",
    gender: "Male",
    birthdate: "",
    email: "",
    address: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const navigate = useNavigate()

  const validatePassword = (password) => {
    const passwordRegex = /^(?=.*\d).{8,}$/; 
    return passwordRegex.test(password);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check password validity
    if (!validatePassword(formData.password)) {
      setMessage("Mật khẩu phải dài ít nhất 8 ký tự và chứa ít nhất 1 số.");
      return;
    }

    try {
      const response = await fetch("http://0.0.0.0:8000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams(formData),
      });

      if (response.ok) {
        setMessage("Đăng ký thành công!");
        setFormData({
          username: "",
          fullname: "",
          gender: "Male",
          birthdate: "",
          email: "",
          address: "",
          password: "",
        });
      } else {
        const errorData = await response.json();
        setMessage(`Đăng ký thất bại: ${errorData.detail || "Lỗi không xác định"}`);
      }
    } catch (error) {
      setMessage("Đăng ký thất bại: Không thể kết nối tới máy chủ.");
    }
  };

  return (
    <div className="register-container">
      <div className="register-form">
        <div className=" register-back">
                  <button
                    className="register-back-"
                    onClick={() => navigate('/')} 
                    >
                    Quay lại
                    </button>
        </div>
        <h1>Form Đăng Ký</h1>
        {message && <div className="message">{message}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
          <div className="form-group">
            <label>Họ và tên:</label>
            <input
              type="text"
              name="fullname"
              value={formData.fullname}
              onChange={handleChange}
              required
            />
          </div>
            <label>Tên đăng nhập:</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Mật khẩu:</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
            {!validatePassword(formData.password) && formData.password && (
              <div className="error">Mật khẩu phải dài ít nhất 8 ký tự và chứa ít nhất 1 số.</div>
            )}
          </div>
          <div className="form-group">
            <label>Giới tính:</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              required
            >
              <option value="Male">Nam</option>
              <option value="Female">Nữ</option>
            </select>
          </div>
          <div className="form-group">
            <label>Ngày sinh:</label>
            <input
              type="date"
              name="birthdate"
              value={formData.birthdate}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Địa chỉ:</label>
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit">Đăng Ký</button>
        </form>
      </div>
    </div>
  );
}

export default RegisterForm;
