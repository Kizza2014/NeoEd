import { useNavigate } from 'react-router-dom';
import "./Notifications.css";
import ChildHeader from '../ChildHeader';

function Notification({ author, date, content }) {
    return (
        <div className="notification-box">
            <div className="notification-header">
                <span className="notification-author">{author}</span>
                <span className="notification-date">
                    <span style={{marginRight:'15px'}}>{date.toLocaleDateString()}</span>
                    <span>{date.toLocaleTimeString()}</span>
                </span>
            </div>
            <div className="notification-content">{content}</div>
        </div>
    );
}

function Notifications({ notifications }) {
    return (
        <>
            <ChildHeader nameHeader="Notifications" />
            <div className="notifications-container">
                <div className="notifications-list">
                    {notifications.map((notification, index) => (
                        <Notification
                            key={index}
                            author={notification.author}
                            date={notification.date}
                            content={notification.content}
                        />
                    ))}
                </div>
            </div>
        </>
    );
}

export default Notifications;