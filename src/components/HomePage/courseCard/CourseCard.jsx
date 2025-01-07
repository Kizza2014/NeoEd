import {React, useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";  
import styles from "./CourseCard.module.css";
import { PiDotsThreeOutlineLight } from "react-icons/pi";
import axios from "axios";
import { ClockLoader, FadeLoader } from "react-spinners";

function UpdateForm({ courseId, showForm, setKey }) {
  const [formData, setFormData] = useState({
    class_name: "",
    subject_name: "",
    description: "",
    class_schedule: "",
    password: "",
    require_password: false,
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    console.log("useEffect");
    const fetchClassroomDetails = async () => {
      setLoading(true);
      try {
        const response = await axios.get(
          `http://localhost:8000/classroom/${courseId}/detail`
        );
        const data = response.data;
        setLoading(false);
        if (JSON.stringify(formData) !== JSON.stringify(data)) {
          setFormData({
            class_name: data.class_name || "",
            subject_name: data.subject_name || "",
            description: data.description || "",
            class_schedule: data.class_schedule || "",
            password: data.password || "",
            require_password: data.require_password || false,
          });
        }
      } catch (error) {
        setLoading(false);
        console.error("Error fetching classroom details:", error);
        alert("Failed to load classroom details.");
      }
    };

    fetchClassroomDetails();
  }, [courseId]);

  const handleUpdate = async() => {
    try {
      setLoading(true);
      const formDataEncoded = new FormData();
        for (const key in formData) {
          formDataEncoded.append(key, formData[key]);
      }
      console.log(formDataEncoded);

      const response = await axios.put(`http://localhost:8000/classroom/${courseId}/update`, formDataEncoded);
      // const response = await axios.post("http://localhost:8000/classroom/create", null, { 
      //   params: {formData}
    // });
      alert("Classroom updated successfully:", response.data);
    } catch (error) {
      alert(error);
    } finally {
      setLoading(false);
      showForm();
      setKey();
    }
  };

  return (
    <div className="newClassDiv">
      {loading && <div className={styles.form_loading}>
            <ClockLoader
              color="#ffb800"
            />
        </div>
      }
      <div style={{ backgroundColor: "#F4A481", textAlign: "center" }}>
        <h2 style={{ justifySelf: "center" }}>Update classroom</h2>
      </div>
      <div className="informationDiv">
        <h2 className="informationTitle">Informations</h2>
      </div>
      <div className="informationForm">
        <label>
          Class Name
          <textarea
            name="class_name"
            rows="1"
            style={{ resize: "none" }}
            placeholder="Cơ sở dữ liệu"
            value = {formData.class_name}
            onChange={handleInputChange}
          ></textarea>
        </label>
        <label>
          Subject Name
          <textarea
            name="subject_name"
            rows="1"
            style={{ resize: "none" }}
            placeholder="MAT9999"
            value = {formData.subject_name}
            onChange={handleInputChange}
          ></textarea>
        </label>
        <label>
          Schedule
          <textarea
            name="class_schedule"
            rows="1"
            style={{ resize: "none" }}
            placeholder="Ngày nghỉ"
            value = {formData.class_schedule}
            onChange={handleInputChange}
          ></textarea>
        </label>
        <label>
          Description
          <textarea
            name="description"
            rows="1"
            style={{ resize: "none" }}
            placeholder="404 Unknown"
            value = {formData.description}
            onChange={handleInputChange}
          ></textarea>
        </label>
        <label>
          Password
          <textarea
            name="password"
            rows="1"
            style={{ resize: "none" }}
            placeholder="None"
            value = {formData.password}
            onChange={handleInputChange}
          ></textarea>
        </label>
      </div>
      <div className="buttonContainer">
        <button className="cancelButton" onClick={showForm}>
          Cancel
        </button>
        <button className="createButton" onClick={handleUpdate}>
          Confirm
        </button>
      </div>
    </div>
  );
}

export const CourseCard = ({ courseDetails, image, setKey }) => {
  const [loading, setLoading] = useState(false);
  const [showDiv, setShowDiv] = useState(false);

  const showUpdateForm = () => {
    setShowDiv(!showDiv);
  };
  
  const { courseTitle, courseId, courseSchedule, instructorInfo, locationInfo } = courseDetails;
  const navigate = useNavigate(); 

  const [showOption, setShowOption] = useState(false);

  const handleShow = () => {
    setShowOption(!showOption);
  }

  const handleClick = () => {
    navigate(`/Classroom/${courseId}`);
  };

  const handleDelete = async () => {
    try {
      setLoading(true);
      await axios.delete(`http://localhost:8000/classroom/${courseId}/delete`, {class_id: courseId});
    } catch (error) {
      console.error("Error creating classroom:", error);
      alert(error);
    } finally {
      console.log(`Deleted course with ID: ${courseId}`);
      setLoading(false);
      setKey();
    }
  };

  if (loading) {
    return(
        <>
        <div className="login-loading">
            <FadeLoader
            color="#ffb800"
            height={50}
            margin={60}
            radius={3}
            width={15}
            />
        </div>
        </>
    )
  }

  return (
    <div className={styles.courseContainer}>
      <div className={styles.courseInfo}>
      {showDiv && <UpdateForm courseId={courseId} showForm={showUpdateForm} setKey={setKey}/>}
        <div className={styles.courseTitle}>
          <div
            style={{width:"80%"}}
          >
            <button
              style={{
                display: 'inline-block',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                width: '100%',
                background: 'none', 
                border: 'none',
                padding: 0,
                textAlign: 'left',
                cursor: 'pointer',
                fontSize: '1.2rem',
                fontWeight: 'bold',
              }}
              onClick={handleClick}
              onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
              onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
            >
              {courseTitle}
            </button>
            <br/>
            <span style={{
                display: 'inline-block', 
                whiteSpace: 'nowrap',   
                overflow: 'hidden',     
                textOverflow: 'ellipsis',
                width: '100%',
                fontSize: '0.7rem',
                fontWeight: 'normal',
              }}>
                {instructorInfo}
            </span>
          </div>
          <div className={styles.course_option} onClick={handleShow}>
            <PiDotsThreeOutlineLight size={27} />
            {showOption && (
              <div className={styles.optionBox}>
                <button onClick={showUpdateForm}>Update</button>
                <button onClick={handleDelete}>Delete</button>
              </div>
            )}
          </div>
        </div>
        <div className={styles.courseImage}>
          <img src={image} alt="Description" />
        </div>
      </div>
    </div>
  );
};
