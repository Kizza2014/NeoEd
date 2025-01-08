import { useNavigate } from 'react-router-dom';
import React, { Suspense, useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import "./Notifications.css";
import FileUploader from '../Attached_files/Attached_files';
import ChildHeader from '../ChildHeader';
import axios from "axios";
import { FilePond, registerPlugin } from 'react-filepond';
import 'filepond/dist/filepond.min.css';
import { FadeLoader, ScaleLoader } from "react-spinners";

function PostForm({handleClick}) {
    const [files, setFiles] = useState([]);
    const { classId } = useParams();
    const [loading, setLoading] = useState(false);
    const [notificationForm, setNotificationForm] = useState({
        title: "",
        content: "",
        // class_id: classId,
        attachments: [],
    });
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setNotificationForm((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleFileChange = (newFiles) => {
        setFiles(newFiles);  // Update files state
        setNotificationForm((prevData) => ({
            ...prevData,
            attachments: newFiles,  // Update form with new files array
        }));
    };
    
    const handleUpload = () => {
        setLoading(true);
        console.log(notificationForm);
        console.log(notificationForm.attachments); // Check if the form data is correct
        // Create FormData object
        const formData = new FormData();
        formData.append('title', notificationForm.title);
        formData.append('content', notificationForm.content);

        // Append files to FormData
        for (let i = 0; i < notificationForm.attachments.length; i++) {
            formData.append('attachments', notificationForm.attachments[i]);
        }

        // Sending the request with FormData
        axios.post(
            `http://localhost:8000/classroom/${classId}/post/create`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
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
              Post content
              <textarea
                name="content"
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

function AddNotification() {
    const [showDiv, setShowDiv] = useState(false);
    const handleClick = () => {
      setShowDiv(!showDiv);
    };


    return (
      <div className="createClassContainer">
        <button className="buttonWrapper" onClick={handleClick}>
          <span> + Tạo thông báo</span>
        </button>
        {showDiv && <PostForm handleClick={handleClick}/>}
      </div>
    );
}

function File_container({ file_name }) {
    return (
        <div className="file-container">
            <div className="file-icon">
                <img src={require('../Exercise/file.png')} alt="File Icon" />
            </div>
            <div className="file-name">
                <p>{file_name}</p>
            </div>
        </div>
    );
}

function Notification({ author, id, date,title, content, checked}) {
    const userId = localStorage.getItem("user_id");
    const [extend, setExtend] = useState(false);
    const [check, setCheck] = useState(checked);
    const onClick = () => {
        // axios.patch('http://localhost:8000/notifications/set-read', 
        //     null, { 
        //         params: {  // Send as query parameters
        //             user_id: userId,
        //             notification_id: id,
        //             read_status: false,
        //         }
        //     }
        // )

        if (!checked) {
            setCheck(true);
            console.log(typeof(userId), typeof(id));
            axios.patch('http://localhost:8000/notifications/set-read', 
                null, { 
                    params: {  // Send as query parameters
                        user_id: userId,
                        notification_id: id,
                        read_status: true,
                    }
                }
            )
            .then(response => {
                console.log('Notification updated successfully:', response.data);
            })
            .catch(error => {
                alert(error);
            });
        }
        setExtend(!extend);
    }
    return (
        <div className="notification-box" >
            <div className="notification-header"
            style={{
                backgroundColor: check ? '#ADA6A6' : '#e0a5a5',
            }}
            onClick={onClick}>
                <span className="notification-author">{author}</span>
                <span className="notification-date">
                    <span style={{ marginRight: '15px' }}>{date.toLocaleDateString()}</span>
                    <span>{date.toLocaleTimeString()}</span>
                </span>
            </div>
            <div className="notification-content">
                {extend ? content : "Title: " + title}
            </div>
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
                        id = {notification.notificationId}
                        date={notification.date}
                        title={notification.title}
                        content={notification.content}
                        checked={notification.checked}
                        onClick={() => onNotificationClick(notification.assignmentId)}
                    />
                ))}
            </div>
        </div>
    );
}

// function Exercise_description({ exercise_name, date, exercise_note, files, onBack }) {
//     return (
//         <div className="exercise_description">
//             <div>
//                 <div className="button-wrapper">
//                     <button className="return-button" onClick={onBack}>
//                         Back to assignments
//                     </button>
//                 </div>
//                 <div className="exercise-header">
//                     <p>{exercise_name}</p>
//                     <p>
//                         <pre>
//                             Date: {date.toLocaleDateString()}   {date.toLocaleTimeString()}
//                         </pre>
//                     </p>
//                 </div>
//                 <div className="exercise-content">
//                     {exercise_note}
//                 </div>
//             </div>
//             <div className="files-grid-container">
//                 <div className="files-grid">
//                     {files.map((file_name, index) => (
//                         <File_container key={index} file_name={file_name} />
//                     ))}
//                 </div>
//             </div>
//         </div>
//     );
// }

function Notification_page({files}) {
    const { classId } = useParams();
    const [notifications, setNotifications] = useState([]);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch notifications (assignments list)
    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const userId = localStorage.getItem('user_id')
                const response = await axios.get('http://127.0.0.1:8000/notifications/user/' + userId);
                const data = response.data;
                const adaptedNotifications = data.map((assignment) => ({
                    author: 'Class: ' + assignment.class_id,
                    date: new Date(assignment.created_at),
                    title: assignment.title,
                    content: assignment.content,
                    notificationId: assignment.notification_id,
                    checked: assignment.read_status,
                }));
                // const response = await axios.get(`http://localhost:8000/classroom/${classId}/post/all`);
                // const data = response.data;
                // const adaptedNotifications = data.map((assignment) => ({
                //     author: assignment.title,
                //     date: new Date(assignment.updated_at),
                //     content: assignment.content,
                //     assignmentId: assignment.id,
                // }));
                console.log(adaptedNotifications);
                setNotifications(adaptedNotifications);
            } catch (error) {
                console.error("Error fetching notifications:", error);
                setError(error)
            } finally{
                setLoading(false);
            }
        };

        if (classId) {
            fetchNotifications();
        }
    
    }, [classId, setError]);

    const handleNotificationClick = async (assignmentId, checked) => {
        try {
            // const response = await axios.get('http://127.0.0.1:8000/notifications/user/user-0bea98bd-a2b8-4d08-ac24-d72d3fdcb0f2');
            // const data = response.data;
            // setSelectedAssignment({
            //     exercise_name: data.author,
            //     date: new Date(data.updated_at),
            //     exercise_note: data.content,
            //     files,
            // });
        } catch (error) {
            console.error("Error fetching assignment details:", error);
            setError(error);
        }
    };

    // const handleBackClick = () => {
    //     setSelectedAssignment(null);
    // };

    if (loading) {
        return (
            <div>
                <ChildHeader nameHeader={"Notifications"} />
                <div style={{
                    display: "flex", 
                    justifyContent: "center", 
                    alignItems: "center",
                    marginTop:"50px",
                }}>
                    <ScaleLoader />
                </div>
            </div>
        );
    }

    if (error) {
        return(
        <>        
            <div>{error.message}</div>
            <AddNotification/>
        </>
        );
    }

    return (
        <div>
            <ChildHeader nameHeader={"Notifications"} />
            <Notifications
                notifications={notifications}
                onNotificationClick={handleNotificationClick}
            />
            <div className="create-notification">
                <AddNotification/>
            </div>
        </div>
    );
}


export default Notification_page;