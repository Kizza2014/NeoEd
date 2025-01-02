import React, { useState } from "react";
import ChildHeader from '../ChildHeader';
import "./Request.css";
import FileUploader from '../Attached_files/Attached_files';

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

function Sended_requests({request_list}){
    const [requests, setRequests] = useState(request_list);

    const deleteRequest = (id) => {
        const updatedRequests = requests.filter((request) => request.id !== id);
        setRequests(updatedRequests);
    };
    const getStateColor = (state) => {
        if (state === "Không duyệt") return "red";
        if (state === "Đã duyệt") return "green";
        return "blue ";
    };
    return(
        <div className="list-request-container">
        <table className="requests-table">
            <thead>
                <tr>
                    <th>STT</th>
                    <th>Yêu cầu</th>
                    <th>Trạng thái </th>
                    <th>Xóa</th>
                </tr>
            </thead>
            <tbody>
                {requests.map((request) => (
                    <tr key={request.id}>
                        <td>{request.id}</td>
                        <td>{request.content}</td>
                        <td style={{ color: getStateColor(request.state) }}>
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
function Request(){
    var requests = [
        { id: 1, content: "Đơn xin nghỉ học ngày 20/11/2022 ", state: "Chưa duyệt " },
        { id: 2, content: "Đơn xin làm lại bài giữa kì I", state: "Đã duyệt" },
        { id: 3, content: "Đơn xin làm lại bài giữa kì II", state: "Không duyệt" },
    ];
    return (
        <div style = {{backgroundColor:"#FFFAFA"}}>
            <ChildHeader nameHeader="Send request" />
            <div className = "request-container">
                <Request_form/>
                <FileUploader/>
            </div>
            <Sended_requests request_list={requests}/>
        </div>
    );
}

export default Request;