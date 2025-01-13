import React, {useState, useEffect} from "react";

import { useParams, useNavigate } from 'react-router-dom';
import axios from "axios";

import { saveAs } from 'file-saver';

import { PiFileSql, PiFilePdf, PiFileZip, PiFileDoc, PiFileImage, PiFileText, PiFile } from "react-icons/pi";

import { BsFiletypeXlsx, BsFiletypeXls } from "react-icons/bs";

import FileUploader from "../../Attached_files/Attached_files";

import { BsThreeDotsVertical } from "react-icons/bs";
import ChildHeader from "../../ChildHeader";
import ScoringInterface from "./ScoringInterface";

 function File_container({ file_name, file_url }) {
    file_name = file_name.split('/').pop();
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

function Exercise_scoring() {
    const navigate = useNavigate(); 
    const { classId, assignmentId } = useParams();
    const [files, setFiles] = useState([]);

    const handleFileChange = (newFiles) => {
        setFiles(newFiles); 
    };

    const [updatedData, setUpdatedData] = useState({
        exercise_name: "",
        date: null,
        exercise_note: "",
        files: [],
    });

    const [assignmentData, setAssignmentData] = useState({
        exercise_name: "",
        date: null,
        exercise_note: "",
        files: [],
    });

    const [isEditing, setIsEditing] = useState(false);
    const handleEditClick = () => {
        setIsEditing(!isEditing);
        setUpdatedData({ ...assignmentData });
    };

    const handleTextChange = (e) => {
        const { name, value } = e.target;
        setUpdatedData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleFileDelete = (index) => {
        setUpdatedData((prevData) => ({
            ...prevData,
            files: prevData.files.filter((_, i) => i !== index),
        }));
    };

    const handleUpdate = async() => {
        try {
            setLoading(true);

            // Create FormData object for multipart/form-data
            const formData = new FormData();
            formData.append("title", updatedData.exercise_name || "");
            formData.append("descriptions", updatedData.exercise_note || "");

            for (let i = 0; i < files.length; i++) {
                formData.append('additional_attachments', files[i]);
            }
            const removalFiles = assignmentData.files.filter(
                (file) => !updatedData.files.some((updatedFile) => updatedFile === file)
            );
    
            removalFiles.forEach((file, index) => {
                formData.append(`removal_attachments`, file.path);
            });

            console.log("FormData Content:", Array.from(formData.entries()));

            // Send the PATCH request
            const response = await axios.put(
                `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/update`,
                formData,
                {
                    params: {
                        token: sessionStorage.getItem('access_token'),
                    },
                }
            );
            console.log("updated success!")
        } catch (error) {
            console.error("Error update assignments:", error);
        } finally {
            setLoading(false);
        }
    }

    const handleDelete = async() => {
        try {
            setLoading(true);
            const response = await axios.delete(
                `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/delete`,
                {
                    params: {
                        token: sessionStorage.getItem('access_token'),
                    },
                }
            );
            alert("Deleted success!");
        } catch (error) {
            console.error("Error fetching assignment details:", error);
        } finally {
            setLoading(false);
        }
    }

    const [isOption, setOption] = useState(false);
    const handleOption = () => {
        setOption(!isOption);
    }

    const [loading, setLoading] = useState(true);

    const onBack = () => {
        navigate(`/c/${classId}/a`);
    };
    
    useEffect(() => {
        const fetchAssignmentDetails = async () => {
            try {
                const response = await axios.get(
                    `http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/detail`,
                    {
                        params: {
                            token: sessionStorage.getItem('access_token'),
                        },
                    }
                );
                const data = response.data;
                setAssignmentData({
                    exercise_name: data.title,
                    date: new Date(data.updated_at),
                    exercise_note: data.descriptions,
                    files: data.attachments,
                });
            } catch (error) {
                console.error("Error fetching assignment details:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchAssignmentDetails();
    }, [classId, assignmentId]);

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
        <div>
            <div className="exercise-overall">
                <div className="exercise-description-container">
                    <div className="Exercise_scoring">
                        <div>
                            <div className="button-wrapper">
                                <button className="return-button" onClick={onBack}>
                                    Back to Assignments
                                </button>
                            </div>
                            <div className="exercise-header">
                                {isEditing ? (
                                    <input
                                        type="text"
                                        name="exercise_name"
                                        style={{
                                            backgroundColor: "transparent",
                                            border: "2px solid #ccc",
                                            borderRadius: "4px",
                                            padding: "8px",
                                            width: "100%",
                                            fontSize: "1rem",
                                        }}
                                        defaultValue={assignmentData.exercise_name}
                                        onChange={handleTextChange}
                                    />
                                ) : (
                                    <p>{assignmentData.exercise_name}</p>
                                )}
                                <pre>
                                    {assignmentData.date
                                        ? `Due date: ${assignmentData.date.toLocaleDateString()} ${assignmentData.date.toLocaleTimeString()}`
                                        : "Loading ..."}
                                </pre>
                                <div>
                                <BsThreeDotsVertical 
                                    onClick={handleOption} 
                                    style={{
                                        cursor: "pointer",
                                    }}
                                />
                                {isOption && (
                                    <div className="option-buttons">
                                        <button 
                                            onClick={handleEditClick} 
                                            style={{ 
                                                cursor: "pointer"
                                            }}
                                        >
                                            Update
                                        </button>
                                        <button 
                                            onClick={handleDelete} 
                                            style={{ 
                                                cursor: "pointer"
                                            }}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                )}
                                </div>
                            </div>
                            <div className="exercise-content">
                                {isEditing ? (
                                    <>
                                    <textarea
                                        name="exercise_note"
                                        rows={5}
                                        defaultValue={assignmentData.exercise_note
                                        }
                                        style={{
                                            backgroundColor: "transparent",
                                            border: "2px solid #ccc",
                                            borderRadius: "4px",
                                            padding: "8px",
                                            width: "100%",
                                            fontSize: "1rem",
                                        }}
                                        onChange={handleTextChange}
                                    />
                                    </>
                                ) : (
                                    <p>{assignmentData.exercise_note}</p>
                                )}
                            </div>
                        </div>
                        <div className="files-grid-container">
                        <div className="files-grid">
                            {(isEditing ? updatedData.files : assignmentData.files).map((file, index) => (
                                <div
                                    key={index}
                                    style={{ display: "flex", alignItems: "center", gap: "10px" }}
                                >
                                    <File_container file_name={file.path} file_url={file.signedURL} />
                                    {isEditing && (
                                        <button
                                            onClick={() => handleFileDelete(index)}
                                            style={{
                                                backgroundColor: "transparent",
                                                border: "none",
                                                color: "red",
                                                fontWeight: "bold",
                                                cursor: "pointer",
                                                fontSize: "18px",
                                            }}
                                        >
                                            X
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                    </div>
                </div>
                <div className="file-uploader-container">
                    <FileUploader files={files} setFiles={handleFileChange} sendHandle={handleUpdate} />
                </div>
            </div>
            <ChildHeader nameHeader={'Scoring'}/>
            <ScoringInterface title={assignmentData.exercise_name} end_at={"" + assignmentData.date.toLocaleTimeString() + "    "+ assignmentData.date.toLocaleDateString() }/>
        </div>
    );
}

export default Exercise_scoring;