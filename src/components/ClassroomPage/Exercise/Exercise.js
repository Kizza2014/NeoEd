import ChildHeader from "../ChildHeader";
import './Exercise.css';

import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, useOutlet, Outlet, useParams } from 'react-router-dom';

import { FadeLoader } from "react-spinners";

import FileUploader from "../Attached_files/Attached_files";

import 'filepond/dist/filepond.min.css';

function PostForm({handleClick}) {
    const [files, setFiles] = useState([]);
    const { classId } = useParams();
    const [loading, setLoading] = useState(false);
    const [notificationForm, setNotificationForm] = useState({
        title: "",
        descriptions: "",
        // class_id: classId,
        start_at: new Date(),
        end_at: new Date(),
    });
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setNotificationForm((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleFileChange = (newFiles) => {
        setFiles(newFiles); 

    };
    
    const handleUpload = () => {
        setLoading(true);
        // Create FormData object
        const formData = new FormData();
        formData.append('title', notificationForm.title);
        formData.append('descriptions', notificationForm.descriptions);

        // Append files to FormData
        for (let i = 0; i < files.length; i++) {
            formData.append('attachments', files[i]);
        }

        // Sending the request with FormData
        axios.post(
            `http://localhost:8000/classroom/${classId}/assignment/create`,
            formData,
            {
                params: {
                    token: sessionStorage.getItem('access_token'),
                },
            }
        )
            .then(response => {
                console.log('Noti created successfully');
                setLoading(false);
            })
            .catch(error => {
                alert('Error uploading data');
                console.error(error);
                setLoading(false);
            });
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
            <h2 style={{ justifySelf: "center" }}>Create post</h2>
          </div>
          <div className="informationDiv">
            <h2 className="informationTitle">Informations</h2>
          </div>
          <div className="informationForm">
            <label>
              Post name
              <textarea 
               name="title"
               rows="1" 
               style={{ resize: "none"}}
               onChange={handleChange}
               placeholder="null"></textarea>
            </label>
            <label>
              Post descriptions
              <textarea
                name="descriptions"
                placeholder="washedup n_g_a ngo"
                rows="5" 
                onChange={handleChange}
                style={{ resize: "vertical" }}
                ></textarea>
            </label>
          </div>
          <div className="file-uploader">
            <FileUploader 
                files = {files}
                setFiles={handleFileChange}
                sendHandle={handleUpload}
            />
            </div>
          <div className="buttonContainer">
            <button className="cancelButton" onClick={handleClick}>
              Cancel
            </button>
            <button className="createButton" onClick={handleUpload}>
              Upload post
            </button>
          </div>
        </div>
      );
}

function AddPost() {
    const [showDiv, setShowDiv] = useState(false);
    const handleClick = () => {
      setShowDiv(!showDiv);
    };
    return (
      <div className="createClassContainer">
        <button className="buttonWrapper" onClick={handleClick}>
          <span> + Tạo post</span>
        </button>
        {showDiv && <PostForm handleClick={handleClick}/>}
      </div>
    );
}

function Notification({ author, date, content, onClick }) {
    return (
        <div className="notification-box">
            <div className="notification-header" onClick={onClick} >
                <span className="notification-author">{author}</span>
                <span className="notification-date">
                    <span style={{ marginRight: '15px' }}>{date.toLocaleDateString()}</span>
                    <span>{date.toLocaleTimeString()}</span>
                </span>
            </div>
            <div className="notification-content">{content}</div>
        </div>
    );
}

function Notifications({ notifications, onNotificationClick }) {
    return (
        <div className="notifications-container">
            <div className="notifications-list">
                {notifications.map((notification, index) => (
                    <Notification
                        key={index}
                        author={notification.author}
                        date={notification.date}
                        content={notification.content}
                        onClick={() => onNotificationClick(notification.assignmentId)}
                    />
                ))}
            </div>
        </div>
    );
}

function Exercise() {
    const [isTeaching, setTeaching] = useState(() => {
        const storedValue = sessionStorage.getItem('isTeaching');
        return storedValue === "true"; // Explicitly convert to boolean
      });

    const { classId } = useParams();
    const navigate = useNavigate();
    const outlet = useOutlet();
    const [notifications, setNotifications] = useState([]);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`http://localhost:8000/classroom/${classId}/assignment/all`,
                    { params: {
                                token: sessionStorage.getItem("access_token"),
                            },
                    }
                );
                const data = response.data;
                const adaptedNotifications = data.map((assignment) => ({
                    author: assignment.author,
                    date: new Date(assignment.end_at),
                    content: assignment.title,
                    assignmentId: assignment.id,
                }));
                setNotifications(adaptedNotifications);
            } catch (Error) {
                console.error("Error fetching notifications:", Error);
                setError(Error)
            } finally{
                setLoading(false);
            }
        };

        if (classId) {
            fetchNotifications();
        }
    
    }, [classId, setError]);

    const handleNotificationClick = async (assignmentId) => {
        if (isTeaching){
            navigate(`/c/t/${classId}/a/${assignmentId}`);
        } else {
            navigate(`/c/${classId}/a/${assignmentId}`);
        }
    };

    const handleBackClick = () => {
        setSelectedAssignment(null);
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

    if (error) {
        return(
        <>        
            <div>{error.message}</div>
            <AddPost/>
        </>
        );
    }

    return (
        <div>
            <ChildHeader nameHeader={"Bài tập"} />
            <div>
                {!outlet && (
                    <>
                <div className="add-button">
                {isTeaching?(<AddPost/>):(<></>) }
                </div>
                    <Notifications
                        notifications={notifications}
                        onNotificationClick={handleNotificationClick}
                    />

                    </>
                )}
                <Outlet />
            </div>
        </div>
    );
}

export default Exercise;
