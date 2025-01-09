import React, { useState, useEffect } from "react";
import axios from "axios";
import { CourseCard } from "../../HomePage/courseCard/CourseCard";
import logo from '../../Utilities/logined_logo.png';
import image from './class_image.png'
import TopBar from "../../Utilities/Top_bar";
import { PacmanLoader } from "react-spinners";
import AddButton from "../../Utilities/AddButton";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHome, faBell, faEnvelope, faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'

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
      setActiveButton(button);
      handleChange();
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
          Joined
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
          Teaching
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
          placeholder="Search..."
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
            color: "black",
            cursor: "pointer",
          }}
        >
          <FontAwesomeIcon icon={faMagnifyingGlass}/>
        </button>
      </div>
    );
  };
  
  const CourseGrid = ({ key, setKey }) => {
    const [loading, setLoading] = useState(true);
    const [classes, setClasses] = useState([]);
    const access_token = sessionStorage.getItem('access_token');
    const [joinedClass, setJoinedClass] = useState([]);
    const [teachingClass, setTeachingClass] = useState([]);
    const [isTeaching, setTeaching] = useState(() => {
      const storedValue = sessionStorage.getItem('isTeaching');
      return storedValue === "true"; // Explicitly convert to boolean
    });
    const [error, setError] = useState('');
    const changeClass = () => {
      setTeaching(!isTeaching);
      sessionStorage.setItem('isTeaching', !isTeaching);
    }
  
    useEffect(() => {
      const fetchClasses = async () => {
        try {
          const response = await axios.get("http://localhost:8000/classroom/all", {
            params: {
              token: access_token,
            },
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
  
      fetchClasses();
    }, []);
  
    useEffect(() => {
      setClasses(isTeaching ? teachingClass : joinedClass);
    }, [isTeaching, teachingClass, joinedClass]);
  
    if (loading) {
      return (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
          <PacmanLoader color="#36d7b7" />
        </div>
      );
    }
  
    if (error) {
      return (
        <div style={{ display: "flex", padding: "30px" }}>
          {error}
        </div>
      );
    }
  
    return (
      <>
        <CheckClasses handleChange={changeClass} />
        <div className="courseGrid">
          {classes.map((classItem, index) => (
            <CourseCard key={index} courseDetails={classItem} image={image} setKey={setKey} />
          ))}
        </div>
      </>
    );
  };
  
  
  
  const TeacherHomePage = () => {
    const [key, setKey] = useState(0);
    const handleTriggerReRender = () => {
      setKey(prev => prev + 1); // Change key to trigger re-render of the child
    };
    return (
      <div className = "container">
        <div className = "slide">
            <img src={logo} className="logo" alt="Description" loading="lazy" />
              <div className="extend_block" style={{ fontWeight: 'bold'}}>
                <div className = "icon-text">
                  <FontAwesomeIcon icon={faHome}/>
                  <span>Lớp học đã lưu trữ </span>
                </div>
              </div>
            <ExtendBlock name = "Thông báo" icon = {faBell} components={["CSDL", "GTS"]} />
            <ExtendBlock name = "Đơn yêu cầu từ học sinh" icon = {faEnvelope} components={["Homework1", "Homework2"]} />
        </div>
        <div className = 'content-div'>
          <TopBar/>
          <p style={{
              marginLeft: '20px',
              fontSize: '24px', 
              fontWeight: 'bold',
            }}>
              Classes
          </p>
          <div className = 'search-bar'>
            <SearchBox/>
            <AddButton setKey={setKey}/>
          </div>
          <CourseGrid key={key} setKey={handleTriggerReRender}/>
        </div>
      </div>
    )
  }
  
  export default TeacherHomePage;