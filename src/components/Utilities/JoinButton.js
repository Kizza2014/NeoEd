import React, { useState } from "react";
import "./AddButton.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";
import { FadeLoader } from "react-spinners";

function ClassForm({ handleClick, setKey }) {
  const userId = localStorage.getItem('user_id');
  const [formData, setFormData] = useState({
    class_id: "",
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
    //   const userResponse = await axios.get(
    //     `http://localhost:8000/user/${userId}/detail`,
    //     {
    //       params: {
    //         token: sessionStorage.getItem("access_token"),
    //       },
    //     }
    //   );
    //   const userName = userResponse.data.username;
       console.log("class_id:", formData.class_id);
        // console.log("username:", userName);
        console.log("token:", sessionStorage.getItem("access_token"));
        const response = await axios.put(
        `http://localhost:8000/classroom/join`,
        null,
        {
          params: {
            invitation_code: formData.class_id,
            token: sessionStorage.getItem("access_token"),
          },
        }
      );
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
        <h2 style={{ justifySelf: "center" }}>Join classroom</h2>
      </div>
      <div className="informationDiv">
        <h2 className="informationTitle">Informations</h2>
      </div>
      <div className="informationForm">
        <label>
          Class Encode
          <textarea
            name="class_id"
            rows="1"
            style={{ resize: "none" }}
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

function JoinButton({setKey}) {
  const [showDiv, setShowDiv] = useState(false);
  const handleClick = () => {
    setShowDiv(!showDiv);
  };
  return (
    <div className="createClassContainer">
      <button className="buttonWrapper" onClick={handleClick}>
      <FontAwesomeIcon icon={faPlus} size="2x"/>
        <span>Tham gia lớp</span>
      </button>
      {showDiv && <ClassForm handleClick={handleClick} setKey={setKey} />}
    </div>
  );
}

export default JoinButton;
