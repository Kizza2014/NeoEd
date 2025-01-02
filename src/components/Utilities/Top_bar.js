import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import "./Top_bar.css";
import exit from "../HomePage/exit_button.png"
import Breadcrumbs from "./Breadcrumbs";

function TopBar() {
    const navigate = useNavigate();
    return (
      <div className="top-bar">
        <Breadcrumbs/>
        <button className="exit-container" onClick={() => navigate('/')}>
          <b>Đăng xuất</b>
          <img src={exit} alt="Đăng xuất" className="exit-icon" />
        </button>
      </div>
    );
  }
  
export default TopBar;