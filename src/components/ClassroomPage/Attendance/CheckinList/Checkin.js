import React, { useState, useEffect } from "react";
import CheckInDetail from "../AttendanceCheck/AttendanceCheck";

import ChildHeader from "../../ChildHeader";
import "./CheckIn.css";
import axios from "axios";
import { useParams } from "react-router-dom";

function Sended_requests({ checkInList }) {
    const [selectedCheckIn, setSelectedCheckIn] = useState(null);

    const handleClose = () => {
        setSelectedCheckIn(null);
    }

    const sortedRequests = [...checkInList].sort(
        (a, b) => new Date(b.ended_at) - new Date(a.ended_at)
    );

    const handleRowClick = (request,index) => {
        console.log("Row clicked:", index);
        setSelectedCheckIn(request);
    };

    return (
        <div className="list-request-container">
            <div>
                <button className="create-checkin-button">
                    Create checkin
                </button>
            </div>
            <table className="requests-table">
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Người tạo</th>
                        <th>Số lượng</th>
                        <th>Thời gian tạo</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedRequests.map((request, index) => (
                        <tr
                            key={request.session_id}
                            className="hoverable-row"
                            style={{cursor:"pointer"}}
                            onClick={() => handleRowClick(request,index)}
                        >
                            <td>{index + 1}</td> {/* Use the array index for the order */}
                            <td>{request.creator}</td>
                            <td>{request.data.attend.length} / {request.data.attend.length + request.data.absent.length} </td>
                            <td>{request.ended_at}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {selectedCheckIn && (
                < CheckInDetail
                    sessionId={selectedCheckIn.session_id}
                    handleClose={handleClose}
                />
            )}
        </div>
    );
}

function CheckinList() {
    const { classId } = useParams();
    const [checkList, setCheckList] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                setLoading(true);
                const response = await axios.get(
                    `http://localhost:8000/checkin/sessions-of-class`,
                    {
                        params: {
                            class_id: classId,
                        },
                    }
                );
                setCheckList(response.data);
                console.log("Fetched data");
            } catch (Error) {
                console.error("Error fetching notifications:", Error);
                setError(Error);
            } finally {
                setLoading(false);
            }
        };

        if (classId) {
            fetchNotifications();
        }
    }, [classId]);

    if (loading) {
        return (
            <div
                style={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    height: "60vh",
                }}
            >
                <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#333" }}>
                    Loading...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ display: "flex", padding: "30px" }}>
                {error}
            </div>
        );
    }

    return (
        <div style={{ backgroundColor: "#FFFAFA" }}>
            <ChildHeader nameHeader="Check in" />
            <Sended_requests checkInList={checkList} />
        </div>
    );
}

export default CheckinList;
