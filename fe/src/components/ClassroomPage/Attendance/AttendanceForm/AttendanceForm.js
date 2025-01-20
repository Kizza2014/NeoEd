// import React, { useState, useEffect } from "react";
// import axios from "axios";
// import { FadeLoader } from "react-spinners";
// import { IoIosReturnLeft } from "react-icons/io";
// function CurrentCheckInDetail({ sessionId, handleClose }) {
//     const [checkInDetails, setCheckInDetails] = useState(null);
//     const [loading, setLoading] = useState(true);
//     const [error, setError] = useState(null);

//     useEffect(() => {
//         const fetchCheckInDetails = async () => {
//             try {
//                 const response = await axios.get(
//                     `http://localhost:8000/checkin/${sessionId}`,
//                     {
//                         params: { session_id: sessionId },
//                     }
//                 );
//                 setCheckInDetails(response.data);
//             } catch (err) {
//                 setError("An error occurred while fetching details.");
//             } finally {
//                 setLoading(false);
//             }
//         };

//         fetchCheckInDetails();
//         const intervalId = setInterval(fetchCheckInDetails, 5000);

//         // Cleanup on unmount
//         return () => clearInterval(intervalId);
//     }, [sessionId]);

//     if (loading) {
//         return (
//             <div className="overlay-container">
//                 <FadeLoader />
//             </div>
//         );
//     }

//     if (error) {
//         return (
//             <div className="overlay-container">
//                 <div className="error-message">{error}</div>
//             </div>
//         );
//     }

//     return (
//         <div className="detail-container">
//             <button
//                 className="close-button"
//                 onClick={handleClose}
//             >
//                 <IoIosReturnLeft size={45} />
//             </button>
//             {sessionData ? (
//                 <div>
//                     <h3>Session Details</h3>
//                     <p><strong>Creator:</strong> {sessionData.creator}</p>
//                     <p><strong>Started At:</strong> {new Date(sessionData.started_at).toLocaleString()}</p>
//                     <p><strong>Ended At:</strong> {new Date(sessionData.ended_at).toLocaleString()}</p>

//                     <h4>Student Attendance</h4>
//                     <div className="table-wrapper">
//                         <table className="attendance-table">
//                             <thead>
//                                 <tr>
//                                     <th>Student ID</th>
//                                     <th>Status</th>
//                                     <th>Action</th>
//                                 </tr>
//                             </thead>
//                             <tbody>
//                                 {[
//                                     ...sessionData.data.absent.map((studentId) => ({
//                                         studentId,
//                                         status: "Absent",
//                                         isCheckedIn: false,
//                                     })),
//                                     ...sessionData.data.attend.map((studentId) => ({
//                                         studentId,
//                                         status: "Present",
//                                         isCheckedIn: true,
//                                     })),
//                                 ]
//                                     .sort((a, b) => a.studentId.localeCompare(b.studentId)) // Sort by studentId
//                                     .map((student) => (
//                                         <tr key={student.studentId}>
//                                             <td>{student.studentId}</td>
//                                             <td style={{ color: student.status === "Absent" ? "red" : "green" }}>
//                                                 {student.status}
//                                             </td>
//                                         </tr>
//                                     ))}
//                             </tbody>
//                         </table>
//                     </div>
//                 </div>
//             ) : (
//                 <p>No session data available.</p>
//             )}
//         </div>
//     );
// }
// export default CurrentCheckInDetail;