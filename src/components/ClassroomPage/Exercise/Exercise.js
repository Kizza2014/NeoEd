import ChildHeader from "../ChildHeader";
import FileUploader from "../Attached_files/Attached_files";
import './Exercise.css';
import React, { Suspense, useState, useEffect } from "react";
import axios from "axios";
import { useParams } from 'react-router-dom';
import { PuffLoader } from "react-spinners";

import { FilePond, registerPlugin } from 'react-filepond';
import 'filepond/dist/filepond.min.css';

function File_container({ file_name }) {
    return (
        <div className="file-container">
            <div className="file-icon">
                <img src={require('./file.png')} alt="File Icon" />
            </div>
            <div className="file-name">
                <p>{file_name}</p>
            </div>
        </div>
    );
}

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

function Notification({ author, date, content, onClick }) {
    return (
        <div className="notification-box" onClick={onClick}>
            <div className="notification-header">
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

function Exercise_description({ exercise_name, date, exercise_note, files, onBack }) {
    return (
        <div className="exercise_description">
            <div>
                <div className="button-wrapper">
                    <button className="return-button" onClick={onBack}>
                        Back to assignments
                    </button>
                </div>
                <div className="exercise-header">
                    <p>{exercise_name}</p>
                    <p>
                        <pre>
                            Due date: {date.toLocaleDateString()}   {date.toLocaleTimeString()}
                        </pre>
                    </p>
                </div>
                <div className="exercise-content">
                    {exercise_note}
                </div>
            </div>
            <div className="files-grid-container">
                <div className="files-grid">
                    {files.map((file_name, index) => (
                        <File_container key={index} file_name={file_name} />
                    ))}
                </div>
            </div>
        </div>
    );
}

function Exercise({files}) {
    const { classId } = useParams();
    const [notifications, setNotifications] = useState([]);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch notifications (assignments list)
    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/classroom/${classId}/post/all`);
                const data = response.data;
                const adaptedNotifications = data.map((assignment) => ({
                    author: assignment.author,
                    date: new Date(assignment.start_at),
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
        setLoading(true);
        try {
            const response = await axios.get(`http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/detail`);
            const data = response.data;
            setSelectedAssignment({
                exercise_name: data.title,
                date: new Date(data.end_at),
                exercise_note: data.descriptions,
                files,
            });
        } catch (error) {
            console.error("Error fetching assignment details:", error);
            setError(error);
        } finally {
            setLoading(false);
        }
    };

    const handleBackClick = () => {
        setSelectedAssignment(null);
    };

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
            <ChildHeader nameHeader={"Assignments"} />
            {selectedAssignment ? (
                <div className="exercise-overall">
                    <Exercise_description
                        exercise_name={selectedAssignment.exercise_name}
                        date={selectedAssignment.date}
                        exercise_note={selectedAssignment.exercise_note}
                        files={selectedAssignment.files}
                        onBack={handleBackClick}
                    />
                    <div>
                        <FileUploader />
                    </div>
                </div>
            ) : (
                <Notifications
                    notifications={notifications}
                    onNotificationClick={handleNotificationClick}
                />
            )}
        </div>
    );
}

export default Exercise;
