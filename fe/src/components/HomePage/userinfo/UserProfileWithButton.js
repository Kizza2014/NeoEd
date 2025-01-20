import React, { useState, useEffect } from "react";
import axios from "axios";
import BackButton from './componentback/BackButton'

import './UserProfileWithButton.css'
import  {BeatLoader } from "react-spinners"

function UserProfile() {
  const [userInfo, setUserInfo] = useState(null); // Thông tin người dùng
  const [formData, setFormData] = useState(null); // Dữ liệu dùng để chỉnh sửa
  const [isEditing, setIsEditing] = useState(false); // Trạng thái: đang chỉnh sửa hay xem
  const [loading, setLoading] = useState(true); // Đang tải dữ liệu
  const [error, setError] = useState(null); // Lỗi

  // Lấy userId từ localStorage
  const getUserIdFromLocalStorage = () => {
    return localStorage.getItem("user_id");
  };

  // Gọi API để lấy thông tin người dùng
  useEffect(() => {
    const fetchUserData = async () => {
      const userId = getUserIdFromLocalStorage();
      if (!userId) {
        setError("Không có User ID trong localStorage.");
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/user/${userId}/detail`);
        setUserInfo(response.data);
        setFormData(response.data); // Đồng bộ formData với thông tin người dùng ban đầu
      } catch (err) {
        setError("Lỗi khi lấy thông tin người dùng.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  // Xử lý thay đổi trong form
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // Xử lý lưu thông tin
  const handleSave = async () => {
    const userId = getUserIdFromLocalStorage();
    if (!userId) {
      setError("Không có User ID trong localStorage.");
      return;
    }
  
    const isDataChanged = Object.keys(formData).some(
      (key) => formData[key] !== userInfo[key]
    );
  
    if (!isDataChanged) {
      alert("Không có thay đổi nào để cập nhật.");
      setIsEditing(false);  // Quay lại chế độ xem
      return;
    }
  
    const updatedUserData = {
      fullname: formData.fullname,
      gender: formData.gender,
      birthdate: formData.birthdate,
      email: formData.email,
      address: formData.address
    };
  
    try {
      const response = await axios.put(`http://localhost:8000/user/${userId}/update`, updatedUserData);
      
      // Lấy dữ liệu mới từ response và cập nhật state
      const { new_info } = response.data;
      
      setUserInfo(new_info);  // Cập nhật thông tin người dùng sau khi chỉnh sửa thành công
      setFormData(new_info);  // Đồng bộ lại formData với userInfo
      setIsEditing(false);  // Chuyển sang chế độ xem
      alert("Cập nhật thông tin thành công!");
    } catch (err) {
      setError("Lỗi khi cập nhật thông tin.");
      console.error(err);
    }
  };
  
  // Xử lý hủy chỉnh sửa
  const handleCancel = () => {
    setFormData(userInfo); // Khôi phục dữ liệu gốc
    setIsEditing(false); // Quay lại chế độ xem
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh' // Chiều cao 100% viewport để căn giữa theo chiều dọc
      }}>
        <BeatLoader
          color="#c97527"
          margin={8}
          size={50}
          speedMultiplier={1}
        />
      </div>

    );
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className = 'container-user-info'>
      <div className = "header">
      <h1>Thông tin cá nhân </h1>
      <BackButton /> 
      </div>
      <div className = "content">
      <div className = "form-group">
        <label>Tên:</label>
        {isEditing ? (
          <input
            type="text"
            name="fullname"
            value={formData.fullname}
            onChange={handleChange}
          />
        ) : (
          <span>{userInfo.fullname}</span>
        )}
      </div>
      <div className = "form-group">
        <label>Giới tính:</label>
        {isEditing ? (
          <input
            type="text"
            name="gender"
            value={formData.gender}
            onChange={handleChange}
          />
        ) : (
          <span>{userInfo.gender}</span>
        )}
      </div>
      <div className = "form-group">
        <label>Ngày sinh:</label>
        {isEditing ? (
          <input
            type="date"
            name="birthdate"
            value={formData.birthdate}
            onChange={handleChange}
          />
        ) : (
          <span>{userInfo.birthdate}</span>
        )}
      </div>
      <div className = "form-group">
        <label>Email:</label>
        {isEditing ? (
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
          />
        ) : (
          <span>{userInfo.email}</span>
        )}
      </div>
      <div className = "form-group">
        <label htmlFor="address">Địa chỉ:</label>
        {isEditing ? (
          <input
            type="text"
            name="address"
            value={formData.address}
            onChange={handleChange}
          />
        ) : (
          <span>{userInfo.address}</span>
        )}
      </div>
      </div>
      
      {isEditing ? (
        <div className = "cancel_save">
          <button className = "cancel" onClick={handleCancel}>Hủy</button>
          <button className = "save" onClick={handleSave}>Lưu thay đổi</button>

        </div>
      ) : (
        <button className = "set-button"onClick={() => setIsEditing(true)}>Chỉnh sửa</button>
      )}
    </div>
  );
}

export default UserProfile;
