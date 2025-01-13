import React, { useState, useEffect } from "react";
import ChildHeader from "../../ChildHeader";
import "./CheckIn.css";
import axios from "axios";
import { useParams } from "react-router-dom";
import { FadeLoader } from "react-spinners";

function Request_form() {
    return (
        <div className="request-form-container">
            <input 
                type="text" 
                placeholder="Enter request name" 
                className="request-name"
            />
            <div className="separator"></div>
            <input 
                type="text" 
                placeholder="Enter request content" 
                className="request-content"
            />
        </div>
    );
}

function Sended_requests({checkInList}){
    const [requests, setRequests] = useState(checkInList);

    const deleteRequest = (id) => {
        const updatedRequests = requests.filter((request) => request.id !== id);
        setRequests(updatedRequests);
    };
    return(
        <div className="list-request-container">
        <table className="requests-table">
            <thead>
                <tr>
                    <th>STT</th>
                    <th>Nguoi tao</th>
                    <th>So luong</th>
                    <th>Xóa</th>
                </tr>
            </thead>
            <tbody>
                {requests.map((request) => (
                    <tr key={request.id}>
                        <td>{request.id}</td>
                        <td>{request.content}</td>
                        <td>
                                {request.state}
                            </td>
                        <td>
                            <button
                                className="delete-button"
                                onClick={() => deleteRequest(request.id)}
                            >
                                🗑
                            </button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
    );
}
function CheckinList(){
    const {classId} = useParams;
    const [checkList, setCheckList] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`http://localhost:8000/checkin/sessions-of-class`,
                    { params: {
                                class_id: classId,
                            },
                    }
                );
                const data = response.data;
                setCheckList(data);
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
    
    }, [classId]);

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
        return (
          <div style={{ display: "flex", padding: "30px" }}>
            {error}
          </div>
        );
      }
    var requests = [
        { id: 1, content: "Đơn xin nghỉ học ngày 20/11/2022 ", state: "Chưa duyệt " },
        { id: 2, content: "Đơn xin làm lại bài giữa kì I", state: "Đã duyệt" },
        { id: 3, content: "Đơn xin làm lại bài giữa kì II", state: "Không duyệt" },
    ];
    return (
        <div style = {{backgroundColor:"#FFFAFA"}}>
            <ChildHeader nameHeader="Check in" />
            <Sended_requests checkInList={checkList}/>
        </div>
    );
}

export default CheckinList;