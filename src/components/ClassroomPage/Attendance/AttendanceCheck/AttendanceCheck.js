import React, { useState, useEffect } from "react";
import { FadeLoader } from "react-spinners";
import axios from "axios";
import { IoIosReturnLeft } from "react-icons/io";
import "./AttendanceCheck.css";

function CheckInDetail({ sessionId, handleClose }) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState();
    const [sessionData, setSessionData] = useState();

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const response = await axios.get(`/checkin/${sessionId}`);
                const fetchedData = response.data;

                // Append fake data for demonstration
                const fakeAbsent = ["user-001", "user-002"];
                const fakeAttend = ["user-003", "user-004"];
                fetchedData.data.absent.push(...fakeAbsent);
                fetchedData.data.attend.push(...fakeAttend);

                // Sort the combined data alphabetically by student ID
                fetchedData.data.absent.sort();
                fetchedData.data.attend.sort();

                setSessionData(fetchedData);
            } catch (err) {
                setError(`An error occurred: ${err.response?.status || "Unknown"} ${err.message}`);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [sessionId]);

    const handleCheckin = (studentId) => {
        console.log(`Handling check-in for student ID: ${studentId}`);
        // Implement the API call or logic to handle check-in here
    };

    if (loading) {
        return (
            <div className="overlay-container">
                <FadeLoader />
            </div>
        );
    }

    if (error) {
        return (
            <div className="overlay-container">
                <div className="error-message">{error}</div>
            </div>
        );
    }

    return (
        <div className="detail-container">
            <button
                className="close-button"
                onClick={handleClose}
            >
                <IoIosReturnLeft size={45} />
            </button>
            {sessionData ? (
                <div>
                    <h3>Session Details</h3>
                    <p><strong>Creator:</strong> {sessionData.creator}</p>
                    <p><strong>Started At:</strong> {new Date(sessionData.started_at).toLocaleString()}</p>
                    <p><strong>Ended At:</strong> {new Date(sessionData.ended_at).toLocaleString()}</p>

                    <h4>Student Attendance</h4>
                    <div className="table-wrapper">
                        <table className="attendance-table">
                            <thead>
                                <tr>
                                    <th>Student ID</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    ...sessionData.data.absent.map((studentId) => ({
                                        studentId,
                                        status: "Absent",
                                        isCheckedIn: false,
                                    })),
                                    ...sessionData.data.attend.map((studentId) => ({
                                        studentId,
                                        status: "Present",
                                        isCheckedIn: true,
                                    })),
                                ]
                                    .sort((a, b) => a.studentId.localeCompare(b.studentId)) // Sort by studentId
                                    .map((student) => (
                                        <tr key={student.studentId}>
                                            <td>{student.studentId}</td>
                                            <td style={{ color: student.status === "Absent" ? "red" : "green" }}>
                                                {student.status}
                                            </td>
                                            <td>
                                                <button
                                                    className="checkin-button"
                                                    onClick={() => handleCheckin(student.studentId)}
                                                    disabled={student.isCheckedIn}
                                                >
                                                    {student.isCheckedIn ? "Already Checked In" : "Check In"}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            ) : (
                <p>No session data available.</p>
            )}
        </div>
    );
}

export default CheckInDetail;
