import "./Attached_files.css"

import React, { useState } from 'react';

function FileUploader() {
    const [files, setFiles] = useState([]);
    const addFiles = (newFiles) => {
        setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    };
    const removeFile = (index) => {
        setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
    };

    return (
        <div className="attach_container">
            <p style={{fontWeight: "bold", textAlign: "center" }}>Attach files</p>
            <div className="file-list">
                {files.map((file, index) => (
                    <div key={index} className="file-item">
                        <span>{file.name}</span>
                        <button onClick={() => removeFile(index)}>✖</button>
                    </div>
                ))}
            </div>
            <label className="attach-button">
                <input
                    type="file"
                    multiple
                    onChange={(e) => addFiles(Array.from(e.target.files))}
                />
                Choose Files
            </label>
            <button className="send-button">
                Send request
            </button>
        </div>
    );
}

export default FileUploader;

