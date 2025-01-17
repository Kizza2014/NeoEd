import "./Attached_files.css"

import React from 'react';

function FileUploader({files, setFiles,sendHandle}) {
    const addFiles = (newFiles) => {
        setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    };
    
    const removeFile = (index) => {
        // Filter out the file at the given index
        const updatedFiles = files.filter((_, i) => i !== index);
        
        // Update the state with the new filtered list
        setFiles(updatedFiles);
    };

    return (
        <div className="attach_container">
            <p style={{fontWeight: "bold", textAlign: "center" }}>Đính kèm thư mục</p>
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
                Tải thư mục lên
            </label>
            <button className="send-button" onClick={sendHandle}>
                Gửi yêu cầu
            </button>
        </div>
    );
}

export default FileUploader;

