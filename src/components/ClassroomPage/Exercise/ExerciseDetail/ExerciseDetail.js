import React, {useState, useEffect} from "react";

import { useParams, useNavigate } from 'react-router-dom';
import axios from "axios";

import { saveAs } from 'file-saver';

import { PiFileSql, PiFilePdf, PiFileZip, PiFileDoc, PiFileImage, PiFileText, PiFile } from "react-icons/pi";

import { BsFiletypeXlsx, BsFiletypeXls } from "react-icons/bs";

import FileUploader from "../../Attached_files/Attached_files";
import Comments from "../../../Utilities/Comments";

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

function Exercise_description() {
    const navigate = useNavigate(); 
    const { classId, assignmentId } = useParams();  

    const [files, setFiles] = useState([]);

    const [submitData, setSubmitData] = useState({
        submitted_files: [],
        grade: null,
    });

    const handleFileChange = (newFiles) => {
        setFiles(newFiles); 
    };

    const [assignmentData, setAssignmentData] = useState({
        exercise_name: "",
        date: null,
        exercise_note: "",
        files: [],
    });
    const student_id = sessionStorage.getItem('user_id');
    const handlesubmit = async() => {
        try {
            setLoading(true);
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('attachments', files[i]);
            }
            console.log(formData);
            const response = await axios.put(
                `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/submit`,
                formData,
                {
                    params: {
                        token: sessionStorage.getItem('access_token'),
                    },
                }
            );
            alert("Summission success!");
        } catch (error) {
            console.error("Error submitting assignment details:", error);
        } finally {
            setLoading(false);
        }
    }

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState();
    const [refreshKey, setRefreshKey] = useState(0);
    const onBack = () => {
        navigate(`/c/${classId}/a`);
    };

    useEffect(() => {
        const fetchAssignmentDetails = async () => {
            try {
                setLoading(true);
                console.log(classId, assignmentId, sessionStorage.getItem('access_token'));
                const response = await axios.get(
                    `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/detail`,
                    {
                        params: {
                            token: sessionStorage.getItem('access_token'),
                        },
                    }
                );
    
                // Fetch assignment submission details
                let submissionData = { grade: null, attachments: [] }; // Default if 404 occurs
                try {
                    const submissionResponse = await axios.get(
                        `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/submission/${student_id}/detail`,
                        {
                            params: {
                                token: sessionStorage.getItem('access_token'),
                            },
                        }
                    );
                    submissionData = submissionResponse.data;
                } catch (error) {
                    if (error.response?.status !== 404) {
                        console.error("Error fetching submission details:", error);
                        setError("An error occurred: " + error.response?.status + " " + error.message);
                    }
                }
    
                setSubmitData(submissionData);
                const data = response.data;
                setAssignmentData({
                    exercise_name: data.title,
                    date: new Date(data.updated_at),
                    exercise_note: data.descriptions,
                    files: data.attachments,
                });
            } catch (error) {
                console.error("Error fetching assignment details:", error);
                setError("An error occurred: " + error.response?.status + " " + error.message);
            } finally {
                setLoading(false);
            }
        };
    
        fetchAssignmentDetails();
    }, [classId, assignmentId, student_id]);
    

    if (error) {
        return (
          <div style={{ display: "flex", padding: "30px" }}>
            {error}
          </div>
        );
      }

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
        <div className="exercise-overall">
            <div className="exercise-description-container">
                <div className="exercise_description">
                    <div>
                        <div className="button-wrapper">
                            <button className="return-button" onClick={onBack}>
                                Back to Assignments
                            </button>
                        </div>
                        <div className="exercise-header">
                            <p>{assignmentData.exercise_name}</p>
                            <pre>
                                {assignmentData.date
                                    ? `Due date: ${assignmentData.date.toLocaleDateString()} ${assignmentData.date.toLocaleTimeString()}`
                                    : "Loading ..."}
                            </pre>
                        </div>
                        <div className="exercise-content">
                            <p>{assignmentData.exercise_note}</p>
                        </div>
                    </div>
                    <div className="files-grid-container">
                    <div className="files-grid">
                        {assignmentData.files.map((file, index) => (
                            <div
                                key={index}
                                style={{ display: "flex", alignItems: "center", gap: "10px" }}
                            >
                                <File_container file_name={file.path} file_url={file.signedURL} />
                            </div>
                        ))}
                    </div>
                </div>
                <Comments
                        key={refreshKey}
                            component= 'assignment'
                            api_parameters={{token: sessionStorage.getItem('access_token')}}
                        />
                </div>

            </div>
            {submitData.grade !== null && <p>Score: {submitData.grade}</p>}
 
                    <div className="file-uploader-container">
                    <FileUploader files={files} setFiles={handleFileChange} sendHandle={handlesubmit} />  
                    </div>


        </div>
    );
}

export default Exercise_description;