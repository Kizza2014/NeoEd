import React, {useState, useEffect} from "react";
import { useParams } from "react-router-dom";
import "./Comments.css"
import axios from "axios";
import { GrSend } from "react-icons/gr";

function Comments({component, api_parameters}){
    const { classId, postId, assignmentId } = useParams();
    const userId = localStorage.getItem('user_id');
    const componentId = component === 'post' ? postId : assignmentId;
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const[loading, setLoading] = useState(false);
    const [error, setError] = useState();
    
    const handleAddComment = async () => {
        try {
            const formData = new FormData();
            formData.append('content', newComment);
            const response =  axios.post(
                `http://localhost:8000/classroom/${classId}/${component}/${componentId}/comment/create`,
                formData,
                {params: api_parameters,}
            );

            var username = localStorage.getItem('username');
            var newCommentObj = {
                username,                
                content: newComment,   
                updated_at: new Date().toISOString() 
            };
    
            // Update comments directly
            setComments([...comments, newCommentObj]);
            // Clear the input field
            setNewComment('');
            console.log("Comment created!");
        } catch (err) {
            setError("An error occurred: " + err.status + " " + err.code);
        }
    }

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form submission
            handleAddComment(); // Call the add comment function
        }
    };

    const handleUpdate = () => {
        console.log("Updated");
    }

    const handleDelete = () => {
        console.log("Updated");
    }

    useEffect(() => {
        const fetchComments = async () => {
            try {
                setLoading(true);
                console.log(classId, component,componentId)
                const response = await axios.get(`http://localhost:8000/classroom/${classId}/${component}/${componentId}/comment/all`, {
                    params: api_parameters,
                });
                const fetchedComments = response.data.map((comment) => ({
                    username: comment.username,
                    content: comment.content,
                    updated_at: comment.updated_at,
                    isUser: comment.user_id === userId
                }));
            
                setComments(fetchedComments);
                console.log("Fetched comments:", response.data);
            } catch (err) {
                setError("An error occurred: " + err.status + " " + err.code);
            } finally {
                setLoading(false);
            }
        };

        if (component && api_parameters) {
            fetchComments();
        }
    }, [component, api_parameters]);

    if (error) {
        return (
            <div style={{ display: "flex", padding: "30px" }}>
                {error}
            </div>
        );
    }

    return (
        <div className="comment-section">
            <h3>Comments</h3>
            {loading ? (
                <p>Loading comments...</p>
            ) : (
                <ul className="comment-list">
                    {comments.map((comment) => (
                        <li key={comment.id} className="comment-item">
                            <p>
                                <strong>{comment.username}:</strong> {comment.content}
                            </p>
                            <span className="comment-date">
                                {new Date(comment.updated_at).toLocaleString()}
                            </span>
                            {comment.isUser && (
                                <div className="comment-actions">
                                    <button onClick={() => handleUpdate(comment.id)}>Update</button>
                                    <button onClick={() => handleDelete(comment.id)}>Delete</button>
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            )}
                        <div className="comment-input-section">
                <input
                    className="comment-input"
                    type="text" 
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Write a comment..."
                    />
                <button className="comment-submit" onClick={handleAddComment}>
                    <GrSend size={23}/>
                </button>
            </div>
        </div>
    );
}

export default Comments;