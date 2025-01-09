import './TeacherClassroomPage.css';
import React from "react";
import logo from '../Utilities/logined_logo.png';
import TopBar from '../Utilities/Top_bar';
import { NavLink, useParams, Outlet, useOutlet } from 'react-router-dom';

import Post from '../ClassroomPage/posts/Posts';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

function TeacherClassroomPage() {
    const { classId } = useParams();
    const outlet = useOutlet();
    return (
      <div className="container">
        <div className="slide">
          <img src={logo} className="logo" alt="Description" loading="lazy" />
          <div className="button-list">
            <NavLink
              to={`/Classroom/${classId}`}
              className={({ isActive }) => (isActive ? "active_class_link" : "")}
              end
            >
              Thông tin lớp học
            </NavLink>
            <NavLink
              to={`/Classroom/${classId}/notifications`}
              className={({ isActive }) => (isActive ? "active_class_link" : "")}
            >
              Thông báo
            </NavLink>
            <NavLink
              to={`/Classroom/${classId}/posts`}
              className={({ isActive }) => (isActive ? "active_class_link" : "")}
            >
              Học liệu
            </NavLink>
            <NavLink
              to={`/Classroom/${classId}/assignment`}
              className={({ isActive }) => (isActive ? "active_class_link" : "")}
            >
              Bài tập
            </NavLink>
            <NavLink
              to={`/Classroom/${classId}/requests`}
              className={({ isActive }) => (isActive ? "active_class_link" : "")}
            >
              Gửi yêu cầu cho giáo viên
            </NavLink>
            <NavLink
              to="/Classroom"
              className={({ isActive }) => (isActive ? "active_class_link" : "")}
              end
            >
              Thoát lớp học
            </NavLink>
          </div>
        </div>
        <div className="content-div">
          <TopBar />
          <Outlet />
          {!outlet && (
              <Post
              />
          )}
        </div>
      </div>
    );
  }
  
  export default TeacherClassroomPage;