import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Slider.css";
import { CourseCard } from "./courseCard/CourseCard";
import logo from '../Utilities/logined_logo.png'
import { useNavigate } from 'react-router-dom';
import TopBar from "../Utilities/Top_bar";
import { PacmanLoader } from "react-spinners";

function ExtendBlock({ name, components }) {
  const [clicked, setClicked] = useState(false);

  const toggleExpand = () => {
    setClicked(!clicked);
  };

  return (
    <div className="extend_block">
      <div onClick={toggleExpand} style={{ fontWeight: 'bold'}}>
        {name}
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

function CheckClasses() {
  const [activeButton, setActiveButton] = useState("button1");

  const handleClick = (button) => {
    setActiveButton(button);
  };

  return (
    <div style={{ display: "flex", justifyContent: "left", gap: "10px", margin: "20px" }}>
      <button
        onClick={() => handleClick("button1")}
        style={{
          padding: "10px 20px",
          backgroundColor: "transparent", // Transparent background
          color: activeButton === "button1" ? "black" : "darkblue",
          fontWeight: "bold", // Bold for both active and inactive
          border: "none", // No border
          cursor: "pointer",
          textDecoration: activeButton === "button1" ? "underline" : "none",
        }}
      >
        Current
      </button>
      <button
        onClick={() => handleClick("button2")}
        style={{
          padding: "10px 20px",
          backgroundColor: "transparent", // Transparent background
          color: activeButton === "button2" ? "black" : "darkblue",
          fontWeight: "bold", // Bold for both active and inactive
          border: "none", // No border
          cursor: "pointer",
          textDecoration: activeButton === "button2" ? "underline" : "none",
        }}
      >
        Complete
      </button>
    </div>
  );
}

const SearchBox = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = () => {
    alert(`Searching for: ${searchQuery}`);
    // Add logic here to handle the search query
  };

  return (
    <div style={{ display: "flex", alignItems: "center", margin: "20px" }}>
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search..."
        style={{
          padding: "10px",
          flex: "1",
          marginRight: "10px",
          borderRadius: "4px",
          border: "1px solid #ccc",
        }}
      />
      <button
        onClick={handleSearch}
        style={{
          padding: "10px 20px",
          color: "black",
          border: "1px solid #ccc",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Search
      </button>
    </div>
  );
};

const courses = [
  {
    courseTitle: "Cơ sở dữ liệu",
    courseSchedule: "Thứ 4, 9h-12h",
    instructorInfo: "Giáo viên: Nguyễn Văn A",
    locationInfo: "Phòng học: 503T5",
  },
  {
    courseTitle: "Giải thuật",
    courseSchedule: "Thứ 2, 14h-16h",
    instructorInfo: "Giáo viên: Trần Văn B",
    locationInfo: "Phòng học: 301T3",
  },
  {
    courseTitle: "Hệ điều hành",
    courseSchedule: "Thứ 5, 10h-12h",
    instructorInfo: "Giáo viên: Lê Thị C",
    locationInfo: "Phòng học: 201T1",
  },
  {
    courseTitle: "Mạng máy tính",
    courseSchedule: "Thứ 3, 8h-10h",
    instructorInfo: "Giáo viên: Nguyễn Văn D",
    locationInfo: "Phòng học: 405T4",
  },
];

const CourseGrid = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [classes, setClasses] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const response = await axios.get("http://localhost:8000/classroom/all");
        const adaptedClasses = response.data.map((classItem) => ({
          courseTitle: classItem.class_name,
          courseId: classItem.id,
          courseSchedule: classItem.class_schedule,
          instructorInfo: `Giáo viên: ${classItem.owner}`,
          locationInfo: "Phòng học: Chưa xác định",
        }));
        setClasses(adaptedClasses);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch classes");
      } finally {
        setLoading(false); 
      }
    };

    fetchClasses();
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center"}}>
        <PacmanLoader color="#36d7b7"/>
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

  // return (
  // <div className="courseGrid">
  //   {classes.map((classItem) => (
  //     <CourseCard key={classItem.id} courseDetails={classItem}/>
  //   ))}
  // </div>
  // );

  return (
    <div className="courseGrid">
      {error && <p className="error">{error}</p>}
      {classes.map((classItem, index) => (
        <CourseCard key={index} courseDetails={classItem} />
      ))}
    </div>
  );

  // return (
  //   <div className="courseGrid">
  //     {courses.map((course, index) => (
  //       <CourseCard key={index} courseDetails={course}/>
  //     ))}
  //   </div>
  // );
};

const Slider = () => {
  return (
    <div className = "container">
      <div className = "slide">
          <img src={logo} className="logo" alt="Description" loading="lazy" />
          <div className="extend_block" style={{ fontWeight: 'bold'}}> Lớp học đã lưu trữ</div>
          <ExtendBlock name = "Thông báo" components={["CSDL", "GTS"]} />
          <ExtendBlock name = "Việc cần làm" components={["Homework1", "Homework2"]} />
          <ExtendBlock name = "Các dự án hiện tại" components={["Project1", "Project2"]} />
      </div>
      <div className = 'content-div'>
        <TopBar/>
        <Joblist tasks={tasks} />
        <p style={{
            marginLeft: '20px',
            fontSize: '24px', 
            fontWeight: 'bold',
          }}>
            Classes
        </p>
        <SearchBox/>
        <CheckClasses/>
        <CourseGrid/>
      </div>
    </div>
  )
}

export default Slider;