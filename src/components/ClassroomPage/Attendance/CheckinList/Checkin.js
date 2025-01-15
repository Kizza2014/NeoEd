import React, { useState, useEffect } from "react";
import CheckInDetail from "../AttendanceCheck/AttendanceCheck";

import ChildHeader from "../../ChildHeader";
import "./CheckIn.css";
import axios from "axios";
import { useParams } from "react-router-dom";
import { HashLoader } from "react-spinners";

function Sended_requests() {
    const num_students = Number(sessionStorage.getItem('num_students'));
    const { classId } = useParams();
    const [selectedCheckIn, setSelectedCheckIn] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [currentSession, setCurrentSession] = useState();
    const [checkList, setCheckList] = useState([]);

    const handleRowClick = (request,index) => {
        console.log("Row clicked:", index);
        setSelectedCheckIn(request);
    };

    const manageCheckIn = async() => {
        if (!currentSession) {
            if (num_students === 0) {
                alert("You need to have students to create check in!!!");
            } else {
                try {
                    console.log("Current id: ", currentSession);
                    setLoading(true);
                    const response = await axios.post(
                        'http://localhost:8000/checkin/new', null,
                        {params: {
                            class_id: classId,
                            creator_id: localStorage.getItem('user_id'),
                        }}
                    );
                    console.log("New session created:", response.data.session_id);
                    // eslint-disable-next-line no-const-assign
                    setCurrentSession(response.data.session_id); // State update is scheduled
                } catch (err) {
                    setError("An error occurred: " + err.status + " " + err.code);
                } finally {
                    setLoading(false);
                }
            }
        } else {
            setLoading(true);
            try {
                console.log(currentSession, classId);
                const response = await axios.post(
                    `http://localhost:8000/checkin/end-session`, null,
                    {params: {
                        session_id: currentSession,
                        class_id: classId,
                    }}
                )
                console.log("Current session ended !");
                setCurrentSession(null);
            } catch (err) {
                setError("An error occurred: " + err.status + " " + err.code);
            } finally {
                setLoading(false);
            }     
        }
    }
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
                const currentCheck = await axios.get(
                    `http://localhost:8000/session/current`,
                    {
                        params: {
                            class_id: classId,
                        },
                    }
                );
                const sortedCheckList = response.data
                    .filter(request => request.data.attend !== undefined)
                    .sort((a, b) => new Date(b.ended_at) - new Date(a.ended_at));
                console.log("Fetched data",sortedCheckList);
                console.log("Current check: ",currentCheck.data);
                setCheckList(sortedCheckList);
                setCurrentSession(currentCheck.data.session_id);

                if (currentCheck.data.session_id) {
                    setCurrentSession(currentCheck.data.session_id);
                }
            } catch (err) {
                setError("An error occurred: " + err.status + " " + err.code);
            } finally {
                setLoading(false);
            }
        };

        if (classId) {
            fetchNotifications();
        }
    }, [classId]);

    if (error) {
        return (
            <div style={{ display: "flex", padding: "30px" }}>
                {error}
            </div>
        );
    }


    return (
        <div className="list-request-container">
            <div>
                {loading ? (
                    <div style={{ marginLeft: "25px", marginTop: "10px" }}>
                        <p>Loading checkIn...</p>
                    </div>
                ) : currentSession ? (
                    <button
                        className="create-checkin-button"
                        onClick={() => manageCheckIn()}
                    >
                        <span className="button-content">
                            Current checkin
                            <HashLoader size={20} />
                        </span>
                    </button>
                ) : (
                    <button
                        className="create-checkin-button"
                        onClick={() => manageCheckIn()}
                    >
                        Create checkin
                    </button>
                )}
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
                    {checkList.map((request, index) => (
                        <tr
                            key={request.session_id}
                            className="hoverable-row"
                            style={{ cursor: "pointer" }}
                            onClick={() => handleRowClick(request, index)}
                        >
                            <td>{index + 1}</td>
                            <td>{request.creator}</td>
                            <td>{request.data.attend?.length ?? "_"} / {request.data.attend?.length + request.data.absent?.length ?? "_"}</td>
                            <td>{request.ended_at}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {selectedCheckIn && (
                <CheckInDetail sessionId={selectedCheckIn.session_id} handleClose={setSelectedCheckIn(null)} />
            )}
        </div>
    );
}

function CheckinList() {
    return (
        <div style={{ backgroundColor: "#FFFAFA"}}>
            <ChildHeader nameHeader="Check in" />
            <Sended_requests/>
        </div>
    );
}

export default CheckinList;
