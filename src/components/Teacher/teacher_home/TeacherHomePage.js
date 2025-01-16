import React, { useState, useEffect } from "react";
import axios from "axios";
import { CourseCard } from "../../HomePage/courseCard/CourseCard";
import { useNavigate } from "react-router-dom";
import useWindowSize from "./SizeContext";

import image from './class_image.png';
import TopBar from "../../Utilities/Top_bar";
import { PacmanLoader } from "react-spinners";

import AddButton from "../../Utilities/AddButton";
import JoinButton from "../../Utilities/JoinButton";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons';
import HomeSideBar from "./HomeSideBar";

const CheckClasses = ({ isTeaching, handleChange }) => (
  <div style={{ display: "flex", justifyContent: "left", gap: "10px", margin: "20px" }}>
    <button
      onClick={() => handleChange(false)}
      style={{
        padding: "10px 20px",
        backgroundColor: "transparent",
        color: !isTeaching ? "black" : "#2353F0",
        fontWeight: "bold",
        border: "none",
        cursor: "pointer",
        textDecoration: !isTeaching ? "underline" : "none",
      }}
    >
      Joined
    </button>
    <button
      onClick={() => handleChange(true)}
      style={{
        padding: "10px 20px",
        backgroundColor: "transparent",
        color: isTeaching ? "black" : "#2353F0",
        fontWeight: "bold",
        border: "none",
        cursor: "pointer",
        textDecoration: isTeaching ? "underline" : "none",
      }}
    >
      Teaching
    </button>
  </div>
);

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
          borderRight: "none",
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
        <FontAwesomeIcon icon={faMagnifyingGlass} />
      </button>
    </div>
  );
};

const CourseGrid = ({ classes, isTeaching, loading, error, updateClasses }) => {
  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
        <PacmanLoader color="#36d7b7" />
      </div>
    );
  }

  if (error) {
    return <div style={{ display: "flex", padding: "30px" }}>{error}</div>;
  }

  return (
    <div className="courseGrid">
      {classes.map((classItem, index) => (
        <CourseCard
          courseDetails={classItem}
          image={image}
          isTeaching={isTeaching ? "c/t" : "c"}
          updateClasses={updateClasses}
        />
      ))}
    </div>
  );
};

const TeacherHomePage = () => {
  const { width } = useWindowSize();
  const [isTeaching, setTeaching] = useState(sessionStorage.getItem("isTeaching") === "true");
  const [joinedClass, setJoinedClass] = useState([]);
  const [teachingClass, setTeachingClass] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const access_token = sessionStorage.getItem("access_token");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchClasses = async () => {
      setLoading(true);
      try {
        const response = await axios.get("http://localhost:8000/classroom/all", {
          params: { token: access_token },
        });

        setJoinedClass(
          response.data.joining_classes.map((classItem) => ({
            courseTitle: classItem.class_name,
            courseId: classItem.id,
            courseSchedule: classItem.class_schedule,
            instructorInfo: `Giáo viên: ${classItem.owner_fullname}`,
            locationInfo: "Phòng học: Chưa xác định",
          }))
        );

        setTeachingClass(
          response.data.teaching_classes.map((classItem) => ({
            courseTitle: classItem.class_name,
            courseId: classItem.id,
            courseSchedule: classItem.class_schedule,
            instructorInfo: `Giáo viên: ${classItem.owner_fullname}`,
            locationInfo: "Phòng học: Chưa xác định",
          }))
        );
      } catch (error) {
        console.error(error);
        if ([422, 401, 403].includes(error.response?.status)) {
          try {
            const fetchNewToken = await axios.post("http://localhost:8000/refresh-token", null, {
              withCredentials: true,
            });
            const newAccessToken = fetchNewToken.data.access_token;
            sessionStorage.setItem("access_token", newAccessToken);
          } catch (refreshError) {
            console.error("Error refreshing token:", refreshError);
            alert("Session expired. Please log in again.");
            navigate("/");
          }
        } else {
          setError("An error occurred: " + error.status || "unknown");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchClasses();
  }, [access_token, navigate]);

  const handleTeachingToggle = (value) => {
    setTeaching(value);
    sessionStorage.setItem("isTeaching", value);
  };

  const classes = isTeaching ? teachingClass : joinedClass;

  return (
    <div>
      {width >= 600 ? (
        <div className="container">
          <HomeSideBar />
          <div className="content-div">
            <TopBar />
            <p
              style={{
                marginLeft: "20px",
                fontSize: "24px",
                fontWeight: "bold",
              }}
            >
              Classes
            </p>
            <div className="search-bar">
              <SearchBox />
              {isTeaching ? (
                <AddButton setCourses={setTeachingClass}/>
              ) : (
                <JoinButton setCourses={setJoinedClass}/>
              )}
            </div>
            <CheckClasses isTeaching={isTeaching} handleChange={handleTeachingToggle} />
            <CourseGrid
              classes={classes}
              isTeaching={isTeaching}
              loading={loading}
              error={error}
              updateClasses={isTeaching ? setTeachingClass : setJoinedClass}
            />
          </div>
        </div>
      ) : (
        <div>
          <h1>haogn</h1>
        </div>
      )}
    </div>
  );
};

export default TeacherHomePage;