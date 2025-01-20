import React, { useState, useEffect } from "react";
import axios from "axios";
import logo from '../../Utilities/logined_logo.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHome, faBell, faEnvelope} from '@fortawesome/free-solid-svg-icons'
import './HomeSideBar.css'
import { PacmanLoader } from "react-spinners";

function ExtendBlock({ name, icon, components }) {
    const [clicked, setClicked] = useState(false);
  
    const toggleExpand = () => {
      setClicked(!clicked);
    };
  
    return (
      <div className="extend_block">
          <div className="icon-text" onClick={toggleExpand} style={{ fontWeight: 'bold'}}>
            <FontAwesomeIcon icon={icon}/>
            <span>{name}</span>
          </div>
        {clicked && (
          <div className = "child-div" style={{marginTop:'5px', marginBottom:"5px"}}>
            {components.map((component) => (
              <button style={{ display: 'block', marginLeft: '20px' }}>
                {component}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  const HomeSideBar = () => {
    const [loading, setLoading] = useState(true);
    const [notifications, setNotifications] = useState([]);
    const [error, setError] = useState();
    const userId = localStorage.getItem('user_id');
    const access_token = sessionStorage.getItem('access_token');
    useEffect(() => {
      const fetchNotification = async () => {
        try {
          const response = await axios.get(`http://localhost:8000/notifications/user/${userId}`);
          setNotifications(response.data);
        } catch (error) {
          console.error("Error fetching data:", error);
          setError("An error occurred: " + error.status + " " + error.code);
        } finally {
          setLoading(false);
        }
      };
      fetchNotification();
    }, [loading, userId]);

    if (loading) {
      return (
        <div className = "slide">
          <img src={logo} className="logo" alt="Description" loading="lazy" />
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
            <PacmanLoader color="#36d7b7" />
          </div>
        </div>
      );
    };

    if (error) {
      return (
        <div className = "slide">
          <img src={logo} className="logo" alt="Description" loading="lazy" />
          <div style={{ display: "flex", padding: "30px" }}>
            {error}
          </div>
        </div>
      );
    };

    return (
        <div className = "slide">
        <img src={logo} className="logo" alt="Description" loading="lazy" />
          <div className="extend_block" style={{ fontWeight: 'bold'}}>
            <div className = "icon-text">
              <FontAwesomeIcon icon={faHome}/>
              <span>Lớp học đã lưu trữ </span>
            </div>
          </div>
            <ExtendBlock name = "Thông báo" icon = {faBell} components={["CSDL", "GTS"]} />
            {notifications.length > 0 && (
              <span
                style={{
                  position: "absolute",
                  top: "-5px",
                  right: "-10px",
                  backgroundColor: "red",
                  color: "white",
                  borderRadius: "50%",
                  padding: "5px 10px",
                  fontSize: "12px",
                  fontWeight: "bold",
                }}
              >
                {notifications.length}
              </span>
            )}
            <ExtendBlock name = "Đơn yêu cầu từ học sinh" icon = {faEnvelope} components={["Homework1", "Homework2"]} />
        </div>
    )
  }

  export default HomeSideBar;