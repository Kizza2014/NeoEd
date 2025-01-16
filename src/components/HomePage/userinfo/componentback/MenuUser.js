import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaUserCircle } from "react-icons/fa";
import BackButton from './BackButton'
import axios from "axios";

const UserMenu = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const [hoveredButton, setHoveredButton] = useState(null);
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleNavigate = (path) => {
    navigate(path);
    setIsDropdownOpen(false); // Đóng dropdown sau khi click
  };

  const handleLogOut = () => {
    axios.post("http://127.0.0.1:8000/logout", null,
      {
        params:{
          access_token: sessionStorage.getItem('access_token'),
        }
      }
    );
    localStorage.clear();
    sessionStorage.clear();
    document.cookie = "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
    navigate('/');
    setIsDropdownOpen(false); // Đóng dropdown sau khi click
  };
  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      {/* Nút hình tròn với biểu tượng người dùng */}
      <button
        onClick={toggleDropdown}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          outline: "none",
        }}
      >
        <FaUserCircle
          style={{
            fontSize: "40px",
            color: "#555",
            borderRadius: "50%",
          }}
        />
      </button>

      {/* Dropdown menu */}
      {isDropdownOpen && (
        <div
          style={{
            position: "absolute",
            top: "50px",
            right: "0",
            background: "#fff",
            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
            borderRadius: "8px",
            width: "150px",
            zIndex: 1000,
          }}
        >
          <button
            onClick={() => handleNavigate("/u")}
            onMouseEnter={() => setHoveredButton("info")}
            onMouseLeave={() => setHoveredButton(null)}
            style={{
              width: "100%",
              padding: "10px",
              border: "none",
              background: hoveredButton === "info" ? "#f0f0f0" : "none",
              textAlign: "left",
              cursor: "pointer",
              fontSize: "14px",
              color: "#333",
              borderBottom: "1px solid #eee",
              transition: "background-color 0.3s",
            }}
          >
            Thông tin cá nhân
          </button>
          <button
            onClick={() => handleLogOut()}
            onMouseEnter={() => setHoveredButton("logout")}
            onMouseLeave={() => setHoveredButton(null)}
            style={{
              width: "100%",
              padding: "10px",
              border: "none",
              background: hoveredButton === "logout" ? "#f0f0f0" : "none",
              textAlign: "left",
              cursor: "pointer",
              fontSize: "14px",
              color: "#333",
              transition: "background-color 0.3s",
            }}
          >
            Đăng xuất
          </button>
        </div>
      )}
    </div>
  );
};

export default UserMenu;