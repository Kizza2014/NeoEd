import { useNavigate } from 'react-router-dom';
import React, { Suspense, useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import "./Notifications.css";
import ChildHeader from '../ChildHeader';
import axios from "axios";
import { FilePond, registerPlugin } from 'react-filepond';
import 'filepond/dist/filepond.min.css';
import { ScaleLoader } from "react-spinners";

function PostForm({handleClick}) {
    const [files, setFiles] = useState([]);

    const handleUpload = () => {
        if (files.length === 0) {
            alert("No files to upload!");
            handleClick();
            return;
        } else {
            alert("Files Uploaded");
            setFiles([]);
            handleClick();
        }
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
               rows="1" 
               style={{ resize: "none"}}
               placeholder="null"></textarea>
            </label>
            <label>
              Post content
              <textarea
                placeholder="washedup n_g_a ngo"
                rows="5" 
                style={{ resize: "vertical" }}
                ></textarea>
            </label>
          </div>
          <div className="file-uploader">
            <FilePond
                files={files}
                onupdatefiles={setFiles}
                allowMultiple={true}
                maxFiles={3}
                instantUpload={false}
                name="files"
                labelIdle='Drag & Drop your files or <span class="filepond--label-action">Browse</span>'
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
        axios.patch('http://localhost:8000/notifications/set-read', 
            null, { 
                params: {  // Send as query parameters
                    user_id: userId,
                    notification_id: id,
                    read_status: false,
                }
            }
        )
        // if (!checked) {
        //     setCheck(true);
        //     console.log(typeof(userId), typeof(id));
        //     axios.patch('http://localhost:8000/notifications/set-read', 
        //         null, { 
        //             params: {  // Send as query parameters
        //                 user_id: userId,
        //                 notification_id: id,
        //                 read_status: true,
        //             }
        //         }
        //     )
        //     .then(response => {
        //         console.log('Notification updated successfully:', response.data);
        //     })
        //     .catch(error => {
        //         alert(error);
        //     });
        // }
        // setExtend(!extend);
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
        // setLoading(true);\
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
                <AddPost/>
            </div>
        </div>
    );
}


export default Notification_page;