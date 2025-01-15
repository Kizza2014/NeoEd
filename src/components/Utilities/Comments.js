import React, {useState, useEffect} from "react";
import { useParams } from "react-router-dom";
import "./Comments.css"
import axios from "axios";
import { GrSend } from "react-icons/gr";
import { IoReorderTwo } from "react-icons/io5";

function Comments({component, api_parameters}){
    const { classId, postId, assignmentId } = useParams();
    const userId = localStorage.getItem('user_id');
    const componentId = component === 'post' ? postId : assignmentId;
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [editingCommentId, setEditingCommentId] = useState(null);
    const [showOptionsFor, setShowOptionsFor] = useState(null);
    const[loading, setLoading] = useState(false);
    const [error, setError] = useState();
    
    const handleAddComment = async () => {
        try {
            setLoading(true);
            const formData = new FormData();
            formData.append('content', newComment);
            const response =  await axios.post(
                `http://localhost:8000/classroom/${classId}/${component}/${componentId}/comment/create`,
                formData,
                {params: api_parameters,}
            );

            var username = localStorage.getItem('username');
            var newCommentObj = {
                commentId: response.data.comment_id,
                username,                
                content: newComment,   
                updated_at: new Date().toISOString(),
                isUser: true,
            };
    
            // Update comments directly
            setComments([...comments, newCommentObj]);
            // Clear the input field
            setNewComment('');
            console.log("Comment created!");
        } catch (err) {
            setError("An error occurred: " + err.status + " " + err.code);
        } finally {
            setLoading(false);
        }
    }

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleAddComment();
        }
    };

    const handleUpdate = async (commentId) => {
        try {
            const formData = new FormData();
            formData.append('content', newComment);
            const response =  axios.put(
                `http://localhost:8000/classroom/${classId}/${component}/${componentId}/comment/${commentId}/update`,
                formData,
                {params: api_parameters,}
            );
    
            // Update comments directly
            setComments((prevComments) =>
                prevComments.map((comment) =>
                    comment.commentId === commentId
                        ? { ...comment, content: newComment, updated_at: new Date().toISOString() }
                        : comment
                )
            );
            setNewComment("");
            setEditingCommentId(null);
            console.log("Comment updated!");
        } catch (err) {
            setError("An error occurred: " + err.status + " " + err.code);
        }
    }

    const handleDelete = async (commentId) => {
        try {
            axios.delete(
                `http://localhost:8000/classroom/${classId}/${component}/${componentId}/comment/${commentId}/delete`,
                {params: api_parameters,}
            );
            setComments((prevComments) =>
                prevComments.filter((comment) => comment.commentId !== commentId)
            );
            console.log("Comment deleted!");
        } catch (err) {
            setError("An error occurred: " + err.status + " " + err.code);
        }
    }

    const handleToggleOptions = (commentId) => {
        setShowOptionsFor(showOptionsFor === commentId ? null : commentId);
        setEditingCommentId(null);
    };

    useEffect(() => {
        const fetchComments = async () => {
            try {
                setLoading(true);
                console.log(classId, component,componentId)
                const response = await axios.get(`http://localhost:8000/classroom/${classId}/${component}/${componentId}/comment/all`, {
                    params: api_parameters,
                });
                const fetchedComments = response.data.map((comment) => ({
                    commentId: comment.id,
                    username: comment.username,
                    content: comment.content,
                    updated_at: comment.updated_at,
                    isUser: comment.user_id === userId
                }));
                fetchedComments.sort((a, b) => new Date(a.updated_at) - new Date(b.updated_at));
                setComments(fetchedComments);
                console.log("Fetched comments:");
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
                                <strong>{comment.username}:</strong> 
                                <span className="comment-date"> 
                                {new Date(comment.updated_at).toLocaleString()}
                                {comment.isUser && (
                                    <div>
                                        <button 
                                        style={{border:"1px solid black"}}
                                        onClick={() => handleToggleOptions(comment.commentId)}>
                                            <IoReorderTwo size={20}/>
                                        </button>
                                        {showOptionsFor === comment.commentId && (
                                            <div className="update-delete-options">
                                                <button onClick={() => setEditingCommentId(comment.commentId)}>Update</button>
                                                <button onClick={() => handleDelete(comment.commentId)}>Delete</button>
                                            </div>
                                        )}  
                                    </div>  
                                )
                                }
                                </span>
                            </p>
                            {editingCommentId === comment.commentId ? (
                                <div>
                                    <input
                                        className="comment-input-edit"
                                        type="text"
                                        defaultValue={comment.content} // Set initial value only
                                        onBlur={(e) => setNewComment(e.target.value)}
                                    />
                                    <button
                                        onClick={() => handleUpdate(comment.commentId)}
                                    >
                                        Confirm
                                    </button>
                                    <button onClick={() => handleToggleOptions()}>
                                        Cancel
                                    </button>
                                </div>
                            ) : (
                                <span className="comment-content">{comment.content}</span>
                            )}
                        </li>
                    ))}
                </ul>
            )}
                        <div className="comment-input-section">
                <input
                    className="comment-input"
                    type="text" 
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