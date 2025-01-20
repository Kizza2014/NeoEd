import React, {useState, useEffect} from "react";

import { useParams, useNavigate } from 'react-router-dom';
import axios from "axios";
import { FadeLoader } from "react-spinners";
import { IoIosReturnLeft } from "react-icons/io";
import { PiFileSql, PiFilePdf, PiFileZip, PiFileDoc, PiFileImage, PiFileText, PiFile } from "react-icons/pi";

import { BsFiletypeXlsx, BsFiletypeXls } from "react-icons/bs";
import { saveAs } from 'file-saver';


function File_container({ file_name, file_url }) {
    const iconMap = {
        pdf: <PiFilePdf size={35} color="black" />,
        doc: <PiFileDoc size={35} color="black" />,
        docx: <PiFileDoc size={35} color="black" />,
        xls: <BsFiletypeXls size={35} color="black" />,
        xlsx: <BsFiletypeXlsx size={35} color="black" />,
        jpg: <PiFileImage size={35} color="black" />,
        png: <PiFileImage size={35} color="black" />,
        txt: <PiFileText size={35} color="black" />,
        zip: <PiFileZip size={35} color="black" />,
        sql: <PiFileSql size={35} color="black" />,
        default: <PiFile size={35} color="black" />,
    };

    const getFileIcon = (fileName) => {
        if (!fileName) {
            return iconMap['default']; // Return default icon if fileName is undefined or empty
        }
        const extension = fileName.split('.').pop().toLowerCase();
        return iconMap[extension] || iconMap['default'];
    };
    
    const handleDownload = () => {
        saveAs(file_url, file_name);
    };

    return (
        <div className="file-container" style={{ cursor: "pointer" }}>
            <div className="file-icon">
                {getFileIcon(file_name)}
            </div>
            <div className="file-name">
                <a
                    href={file_url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    onClick={handleDownload}
                    style={{ color: "black" }}
                    onMouseEnter={(e) => e.target.style.textDecoration = "underline"}
                    onMouseLeave={(e) => e.target.style.textDecoration = "none"}
                >   
                    {file_name}
                </a>
            </div>
        </div>
    );
}

function SubmissionDetail({student_id, student_name, status, submission_date, handleClose, onGradeUpdate}) {
    const { classId, assignmentId } = useParams();
    const [loading, setLoading] = useState(false);
    const [detail,setDetail] = useState(
        {
            attachments: {
                path:"",
                signedURL:"",
            },
        }
    );

    const [score, setScore] = useState(0);
    const handleScoreChange = (e) => {
        const value = e.target.value;
        setScore(value); 
    };

    const handleScore = async() => {
        try {
            console.log(score);
            const data = new URLSearchParams();
            data.append("grade", score);
            const response = axios.put(
                `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/submission/${student_id}/grade`,
                data,
                {
                    params: {
                        token: sessionStorage.getItem('access_token'),
                    },
                }
            );
            onGradeUpdate(student_id, score);
            console.log(response.data);
            alert("Scored");
        } catch (error) {
            console.error("Error:", error);
        } finally {
        }
    }
    useEffect(() => {
        const fetchSubmissionDetails = async () => {
            try {
                setLoading(true);
                console.log(classId,assignmentId,student_id);
                const response = await axios.get(
                    `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/submission/${student_id}/detail`,
                    {
                        params: {
                            token: sessionStorage.getItem('access_token'),
                        },
                    }
                );
                console.log(response.data);
                setDetail(response.data);
            } catch (error) {
                console.error("Error fetching assignment details:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchSubmissionDetails();
    }, [assignmentId, classId]);
    
    return (
        <>
        {loading ? (
            <div 
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'fixed',
                    top: '50%',
                    left: '50%',
                    background: 'transparent',  
                    zIndex: 9999,
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                <FadeLoader />
            </div>
        ) : (
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'fixed',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    padding: '30px',
                    paddingLeft: '20px',
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    color: 'rgb(0, 0, 0)',
                    border: '1px solid black',
                    minWidth: '40vw', 
                    minHeight: '50vh',
                    zIndex: 9999,
                }}
            >
                <button
                    style={{
                        position: 'absolute',
                        top: '10px',
                        right: '7px',
                        background: 'transparent',
                        border: 'none',
                        fontSize: '16px',
                        color: 'black',
                        cursor: 'pointer',
                    }}
                    onClick={handleClose}
                    > <IoIosReturnLeft size={45}/> 
                </button>
                <p>Tên sinh viên: {student_name}</p>
                <p>Trạng thái: {status}</p>
                <p>Thời gian nộp: {submission_date} </p>
                <h2>Nộp bài:</h2>
                <div className="files-grid-container">
                    <div className="files-grid">
                        {(Array.isArray(detail.attachments) ? detail.attachments : []).map((file, index) => (
                            <div key={index}>
                                <File_container 
                                    file_name={file?.path || "Unknown File"} 
                                    file_url={file?.signedURL || "#"} 
                                />
                            </div>
                        ))}
                    </div>
                </div>
                <div style={{ marginTop: "20px", display: "flex", flexDirection: "column", width: "100%" }}>
                    <label
                        htmlFor="score-input"
                        style={{
                            fontSize: "16px",
                            marginBottom: "10px",
                        }}
                    >
                        Điểm (Thang 100):
                    </label>
                    <div style={{ display: "flex", flexDirection: "row", width: "100%", height:'50px', gap:'5%' }}>
                        <input
                            type="number"
                            id="score-input"
                            name="score"
                            onChange = {handleScoreChange}
                            placeholder="Enter score"
                            min="0"
                            max="100"
                            style={{
                                padding: "5px",
                                fontSize: "16px",
                                width: "70%",
                                borderRadius: "4px",
                                border: "1px solid #ccc",
                            }}
                        />
                        <button
                            style={{
                                marginLeft: "10px",
                                padding: "6px 12px",
                                fontSize: "16px",
                                width: "30%",
                                backgroundColor: "#F4A481",
                                color: "white",
                                border: "none",
                                borderRadius: "4px",
                                cursor: "pointer",
                            }}
                            onClick={() => {
                                // Handle score submission logic here
                                handleScore();
                            }}
                        >
                            Confirm
                        </button>
                    </div>
                </div>
            </div>
        )}
        </>
    );    
}

function ScoringInterface({ title, end_at }) {
    const [submissionList, setSubmissionList] = useState([]);
    const { classId, assignmentId } = useParams();
    const [loading, setLoading] = useState(false);
    const [submissionStats, setSubmissionStats] = useState({ submitted: 0, total: 0 });
    const [selectedSubmission, setSelectedSubmission] = useState(null);
    
    const onGradeUpdate = (studentId, newGrade) => {
        setSubmissionList((prevList) =>
            prevList.map((submission) =>
                submission.user_id === studentId
                    ? { ...submission, grade: newGrade }
                    : submission
            )
        );
    };

    const handleClose = () => {
        setSelectedSubmission(null);
    }
    useEffect(() => {
        const fetchSubmissionDetails = async () => {
            try {
                setLoading(true);
                const response = await axios.get(
                    `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/submission/all`,
                    {
                        params: {
                            token: sessionStorage.getItem('access_token'),
                        },
                    }
                );
                const submittedCount = response.data.filter(
                    (student) => student.submitted
                ).length;
                const totalCount = response.data.length;

                const sortedData = response.data.sort((a, b) => {
                    if (a.username < b.username) return -1;
                    if (a.username > b.username) return 1;
                    return 0;
                });

                setSubmissionList(sortedData);
                setSubmissionStats({ submitted: submittedCount, total: totalCount });
            } catch (error) {
                console.error("Error fetching assignment details:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchSubmissionDetails();
    }, [classId, assignmentId]);

    const getStatus = (submittedAt) => {
        if (!submittedAt) return "Not Submitted";
        const submittedDate = new Date(submittedAt);
        const deadlineDate = new Date(end_at);
        return submittedDate <= deadlineDate ? "Completed" : "Late";
    };

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

    return (
        <div style={{ padding: "20px" }}>
            <p>Số lượng bài nộp: {submissionStats.submitted} / {submissionStats.total}</p>
            <p>Hạn nộp: {end_at}</p>
            <table
                style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    marginTop: "20px",
                }}
            >
                <thead>
                    <tr style={{ borderBottom: "2px solid #ccc" }}>
                        <th style={{ textAlign: "left", padding: "10px" }}>Tên thành viên</th>
                        <th style={{ textAlign: "left", padding: "10px" }}>Thời gian nộp</th>
                        <th style={{ textAlign: "left", padding: "10px" }}>Trạng thái </th>
                        <th style={{ textAlign: "left", padding: "10px" }}>Điếm số</th>
                    </tr>
                </thead>
                <tbody>
                    {submissionList.map((submission, index) => (
                        <tr
                            key={index}
                            onClick={() => setSelectedSubmission(submission)}
                            style={{
                                borderBottom: "1px solid #eee",
                                background: index % 2 === 0 ? "#f9f9f9" : "white",
                                cursor: "pointer", // Makes the row look clickable
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.textDecoration = "underline";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.textDecoration = "none";
                            }}
                        >
                            <td style={{ padding: "10px" }}>{submission.username}</td>
                            <td style={{ padding: "10px" }}>
                                {submission.submitted_at
                                    ? new Date(submission.submitted_at).toLocaleString()
                                    : "Not Submitted"}
                            </td>
                            <td style={{ padding: "10px" }}>{getStatus(submission.submitted_at)}</td>
                            <td style={{ padding: "10px" }}>
                                {submission.grade ? `${submission.grade} / 100` : " _ /100"}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {selectedSubmission && (
                <SubmissionDetail
                    student_id={selectedSubmission.user_id}
                    student_name={selectedSubmission.username}
                    status={getStatus(selectedSubmission.submitted_at)}
                    submission_date={selectedSubmission.submitted_at ? new Date(selectedSubmission.submitted_at).toLocaleString() : "Not Submitted"}
                    files={selectedSubmission.files ?? []}
                    handleClose={handleClose}
                    onGradeUpdate={onGradeUpdate}
                />
            )}
        </div>
    );
}

export default ScoringInterface;
