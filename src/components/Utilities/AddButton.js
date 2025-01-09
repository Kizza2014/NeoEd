import React, { useState } from "react";
import "./AddButton.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";
import { FadeLoader } from "react-spinners";

function ClassForm({ handleClick, setKey }) {
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
  const handleCreate = async () => {
    try {
      setLoading(true);
      const formDataEncoded = new URLSearchParams();
        for (const key in formData) {
          formDataEncoded.append(key, formData[key]);
      }
      console.log(formDataEncoded);

      const response = await axios.post(
        "http://localhost:8000/classroom/create",
        formDataEncoded,
        {
            params: {
                token: sessionStorage.getItem("access_token"),
           }
        }
    );
      // const response = await axios.post("http://localhost:8000/classroom/create", null, { 
      //   params: {formData}
    // });
      console.log("Classroom created successfully:", response.data);
    } catch (error) {
      console.error("Error creating classroom:", error);
      alert(error);
    } finally {
      handleClick();
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
    <div className="newClassDiv">
      <div style={{ backgroundColor: "#F4A481", textAlign: "center" }}>
        <h2 style={{ justifySelf: "center" }}>Create classroom</h2>
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
            onChange={handleInputChange}
          ></textarea>
        </label>
      </div>
      <div className="buttonContainer">
        <button className="cancelButton" onClick={handleClick}>
          Cancel
        </button>
        <button className="createButton" onClick={handleCreate}>
          Create
        </button>
      </div>
    </div>
  );
}

function AddButton({setKey}) {
  const [showDiv, setShowDiv] = useState(false);
  const handleClick = () => {
    setShowDiv(!showDiv);
  };
  return (
    <div className="createClassContainer">
      <button className="buttonWrapper" onClick={handleClick}>
      <FontAwesomeIcon icon={faPlus} size="2x"/>
        <span>Tạo lớp</span>
      </button>
      {showDiv && <ClassForm handleClick={handleClick} setKey={setKey} />}
    </div>
  );
}

export default AddButton;
