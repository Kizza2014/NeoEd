import React, { useState, useEffect } from "react";
import axios from "axios";
import { CourseCard } from "../../HomePage/courseCard/CourseCard";

import useWindowSize from "./SizeContext";

import image from './class_image.png'
import TopBar from "../../Utilities/Top_bar";
import { PacmanLoader } from "react-spinners";

import AddButton from "../../Utilities/AddButton";
import JoinButton from "../../Utilities/JoinButton";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'
import HomeSideBar from "./HomeSideBar";
import './TeacherHomePage.css'
import { useNavigate } from "react-router-dom";

const tasks = [
  { job: "Bài tập: Giải tích 3", date: "2024-12-22" },
  { job: "Nhiệm vụ: Tìm hiểu MongoDB", date: "2024-12-23" },
  { job: "Bài tập lập trình cho khoa học ", date: "2024-12-24" },
  { job: "Bài tập lập trình cho khoa học 2 ", date: "2024-12-26" }
];

tasks.sort((a, b) => new Date(a.date) - new Date(b.date));


function Joblist({ tasks = [] }) {
  const getRowStyle = (date) => {
    const today = new Date();
    const taskDate = new Date(date);

    const diffInDays = Math.ceil((taskDate - today) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) {
      return { backgroundColor: '#FFAAAB' };
    } else if (diffInDays > 0 && diffInDays <= 3) {
      return { backgroundColor: '#FFF0B9' };
    } else {
      return {};
    }
  };

  return (
    <>
      <div className="jobs">
        <b>Things to do</b> <br />
        {tasks.length} jobs
        <table className="table">
          <thead>
            <tr>
              <th>Job</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task, index) => (
              <tr key={index} style={getRowStyle(task.date)}>
                <td>{task.job}</td>
                <td>{task.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function CheckClasses({handleChange}) {
  const isTeaching = sessionStorage.getItem('isTeaching') === "true";
  const [activeButton, setActiveButton] = useState((isTeaching ? 'button2' : 'button1'));

  const handleClick = (button, isTeaching) => {
    if (activeButton !== button) {
      setActiveButton(button);
      handleChange();
    }
  };


  return (
    <div style={{ display: "flex", justifyContent: "left", gap: "10px", margin: "20px" }}>
      <button
        onClick={() => handleClick("button1", false)}
        style={{
          padding: "10px 20px",
          backgroundColor: "transparent", // Transparent background
          color: activeButton === "button1" ? "black" : "#2353F0",
          fontWeight: "bold", // Bold for both active and inactive
          border: "none", // No border
          cursor: "pointer",
          textDecoration: activeButton === "button1" ? "underline" : "none",
        }}
      >
        Lớp đang tham gia
      </button>
      <button
        onClick={() => handleClick("button2", true)}
        style={{
          padding: "10px 20px",
          backgroundColor: "transparent", // Transparent background
          color: activeButton === "button2" ? "black" : "#2353F0",
          fontWeight: "bold", 
          border: "none", 
          cursor: "pointer",
          textDecoration: activeButton === "button2" ? "underline" : "none",
        }}
      >
        Lớp đang quản lý
      </button>
    </div>
  );
}

const SearchBox = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = () => {
    alert(`Searching for: ${searchQuery}`);
  };

  return (
    <div style={{ display: "flex", alignItems: "center", margin: "20px" }}>
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Tìm kiếm..."
        style={{
          paddingLeft: "10px",
          borderRadius: "25px 0px 0px 25px",
          border: "1px solid #000",
          borderRight:"none",
          flex: "1",
          width: "713px",
          height: "40px",
          boxSizing: "border-box",

        }}
      />
      <button
        onClick={handleSearch}
        style={{
          borderRadius: "0px 25px 25px 0px",
          border: "1px solid #000",
          width: "53px",
          height: "40px",
          background: "white",
          color: "black",
          cursor: "pointer",
        }}
      >
        <FontAwesomeIcon icon={faMagnifyingGlass}/>
      </button>
    </div>
  );
};

const CourseGrid = ({ uniqueKey, setKey }) => {
  const [loading, setLoading] = useState(true);
  const [classes, setClasses] = useState([]);
  const access_token = sessionStorage.getItem('access_token');
  const [joinedClass, setJoinedClass] = useState([]);
  const [teachingClass, setTeachingClass] = useState([]);
  const [isTeaching, setTeaching] = useState(() => sessionStorage.getItem('isTeaching') === "true");
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchClasses = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://localhost:8000/classroom/all", {
        params: { token: access_token },
      });

      const joiningClasses = response.data.joining_classes.map((classItem) => ({
        courseTitle: classItem.class_name,
        courseId: classItem.id,
        courseSchedule: classItem.class_schedule,
        instructorInfo: `Giáo viên: ${classItem.owner_fullname}`,
        locationInfo: "Phòng học: Chưa xác định",
      }));
      setJoinedClass(joiningClasses);

      const teachingClasses = response.data.teaching_classes.map((classItem) => ({
        courseTitle: classItem.class_name,
        courseId: classItem.id,
        courseSchedule: classItem.class_schedule,
        instructorInfo: `Giáo viên: ${classItem.owner_fullname}`,
        locationInfo: "Phòng học: Chưa xác định",
      }));
      setTeachingClass(teachingClasses);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("An error occurred: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClasses();
  }, [access_token]);

  useEffect(() => {
    setClasses(isTeaching ? teachingClass : joinedClass);
  }, [isTeaching, teachingClass, joinedClass]);

  const handleUpdateCourses = () => {
    fetchClasses(); // Gọi lại API để cập nhật danh sách
    setKey(prev => prev + 1); // Trigger re-render
  };

  return (
    <>
      <CheckClasses handleChange={() => {
        setTeaching(!isTeaching);
        sessionStorage.setItem('isTeaching', !isTeaching);
      }} />
      <div className="button-check-class">
        {isTeaching ? <AddButton setKey={handleUpdateCourses} /> : <JoinButton setKey={handleUpdateCourses} />}
      </div>
      <div className="courseGrid">
        {classes.map((classItem, index) => (
          <CourseCard
            key={index}
            courseDetails={classItem}
            image={image}
            setKey={handleUpdateCourses}
            isTeaching={isTeaching ? "c/t" : "c"}
          />
        ))}
      </div>
    </>
  );
};



const TeacherHomePage = () => {
  const [key, setKey] = useState(0);
  const { width } = useWindowSize(); 
  const isTeaching = sessionStorage.getItem('isTeaching') === "true";
  const navigate = useNavigate();
  useEffect(() => {
    const access_token = sessionStorage.getItem('access_token');
    if (!access_token) {
      navigate('/'); 
    }
  }, [navigate]);
  const handleTriggerReRender = () => {
    setKey(prev => prev + 1); 
  };
  return (
    <div>
        <div className = "container">
        <HomeSideBar/>
        <div className = 'content-div'>
          <TopBar/>
          <p style={{
              marginLeft: '20px',
              fontSize: '24px', 
              fontWeight: 'bold',
            }}>
              Lớp học
          </p>
          <div className = 'search-bar'>
            <SearchBox/>
          </div>
          <CourseGrid uniqueKey={key} setKey={handleTriggerReRender}/>
        </div>
      </div>


    </div>
  )
}

export default TeacherHomePage;