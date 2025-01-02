import ChildHeader from "../ChildHeader";
import FileUploader from "../Attached_files/Attached_files";
import './Exercise.css';
import React, { useState } from "react";

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

const notifications = [
    {
        author: "Admin",
        date: new Date(),
        content: "Your assignment has been graded.",
    },
    {
        author: "System",
        date: new Date(),
        content: "The server will be down for maintenance at midnight.",
    },
    {
        author: "Teacher",
        date: new Date(),
        content: "Class has been rescheduled to tomorrow at 9 AM.",
    },
];

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
                        onClick={onNotificationClick}
                    />
                ))}
            </div>
        </div>
    );
}

function Exercise_description({ exercise_name, date, exercise_note, files,onBack}) {
    return (
        <div className="exercise_description">
            <div>
                <div className="button-wrapper">
                    <button className="return-button" onClick={onBack}>
                        Back to Notifications
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
            <div className = "files-grid-container">
                <div className="files-grid">
                    {files.map((file_name) => (
                        <File_container file_name={file_name}/>
                    ))}
                </div>
            </div>
        </div>
    );
}

function Exercise({ exerciseData ,onBack }) {
    const { exercise_name, date, exercise_note, files } = exerciseData;

    const [showExercise, setShowExercise] = useState(false);

    const handleNotificationClick = () => {
        setShowExercise(true);
    };

    const handleBackClick = () => {
        setShowExercise(false);
    };

    return (
        <div>
            <ChildHeader nameHeader={"Exercise"} />
            {showExercise ? (
                <div className="exercise-overall">
                    <Exercise_description
                        exercise_name={exercise_name}
                        date={date}
                        exercise_note={exercise_note}
                        files={files}
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