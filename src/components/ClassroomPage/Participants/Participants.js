import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Paticipants.css';
import { useParams } from 'react-router-dom';
import ChildHeader from '../ChildHeader'
const Participants = () => {
  const isTeaching = sessionStorage.getItem('isTeaching') ==="true"
  const [loading, setLoading] = useState(true);
  const [teachers, setTeachers] = useState([]);
  const [students, setStudents] = useState([]);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [newParticipant, setNewParticipant] = useState({ username: '', role: 'student' });
  const [formError, setFormError] = useState(null); // Lỗi cụ thể của form
  const { classId } = useParams();
  // Lấy dữ liệu các thành viên
  useEffect(() => {
    const fetchParticipants = async () => {
      try {
        setLoading(true);
        const token = sessionStorage.getItem('access_token');
        const response = await axios.get(
          `http://0.0.0.0:8000/classroom/${classId}/participant/all?token=${token}`
        );
        setTeachers(response.data.teachers || []);
        setStudents(response.data.students || []);
      } catch (err) {
        console.error('Lỗi khi lấy dữ liệu:', err);
        setError('Không thể tải dữ liệu');
      } finally {
        setLoading(false);
      }
    };

    fetchParticipants();
  }, [classId]);

  const handleAdd = async () => {
    setFormError(null);
    setSuccessMessage(null);
    if (!newParticipant.username.trim()) {
      setFormError('Vui lòng nhập tên người dùng');
      return;
    }
  
    setFormError(null); // Xóa lỗi cũ
    const token = sessionStorage.getItem('access_token');
    const endpoint =
      newParticipant.role === 'teacher'
        ? `http://0.0.0.0:8000/classroom/${classId}/participant/add-teacher/${newParticipant.username}?token=${token}`
        : `http://0.0.0.0:8000/classroom/${classId}/participant/add-student/${newParticipant.username}?token=${token}`;
  
    try {
      const response = await axios.put(endpoint);
  
      // Nếu API trả về thành công
      if (response.status === 200) {
        if (newParticipant.role === 'teacher') {
          setTeachers((prev) => [...prev, { username: newParticipant.username }]);
        } else {
          setStudents((prev) => [...prev, { username: newParticipant.username }]);
        }
        setSuccessMessage(
          `Đã thêm ${newParticipant.role === 'teacher' ? 'giáo viên' : 'học sinh'} thành công.`
        );
        setNewParticipant({ username: '', role: 'student' }); // Reset form
      }
    } catch (err) {
      console.error('Lỗi khi thêm thành viên:', err);
  
      if (err.response && err.response.status === 403) {
        if (err.response.data.detail === 'Forbidden. User is already in this classroom') {
          setFormError('Người dùng đã có trong lớp học.');
        } else {
          setFormError('Bạn không có quyền thực hiện hành động này.');
        }
      } else if (err.response) {
        setFormError(`Lỗi: ${err.response.data.detail || 'Không thể thêm thành viên.'}`);
      } else {
        setFormError('Đã xảy ra lỗi không xác định. Vui lòng thử lại.');
      }
    }
  };
  
  // Xử lý xóa thành viên
  const handleRemove = async (username, role) => {
    setFormError(null);
    setSuccessMessage(null);
    if (!window.confirm('Bạn có chắc chắn muốn xóa?')) return;
    
    try {
      const token = sessionStorage.getItem('access_token');
      const endpoint =
        role === 'teacher'
          ? `http://0.0.0.0:8000/classroom/${classId}/participant/remove-teacher/${username}?token=${token}`
          : `http://0.0.0.0:8000/classroom/${classId}/participant/remove-student/${username}?token=${token}`;
  
      const response = await axios.delete(endpoint);
  
      // Kiểm tra phản hồi từ API
      if (response.status === 200) {
        // Cập nhật danh sách thành viên sau khi xóa
        if (role === 'teacher') {
          setTeachers((prev) => prev.filter((teacher) => teacher.username !== username));
        } else if (role === 'student') {
          setStudents((prev) => prev.filter((student) => student.username !== username));
        }
  
        // Hiển thị thông báo thành công
        setSuccessMessage(`Đã xóa ${role === 'teacher' ? 'giáo viên' : 'học sinh'} thành công.`);
        setFormError(null);  // Clear error if successful
        setTimeout(() => setSuccessMessage(null), 3000); // Ẩn thông báo sau 3 giây
      } else {
        setFormError('Không thể xóa thành viên. Vui lòng thử lại.');
        setSuccessMessage(null);  // Clear success message if error occurs
      }
    } catch (err) {
      console.error('Lỗi khi xóa thành viên:', err);

      if (err.response && err.response.status === 403) {
        if (err.response.data.detail === "Forbidden. Owner cannot be removed from classroom") {
          setFormError('Không thể xóa. Thành viên này là chủ phòng học.');
        } else {
          setFormError('Không thể xóa. Người dùng đã có trong lớp hoặc có lỗi khác.');
        }
      } else {
        setError('Không thể xóa. Vui lòng thử lại.');
      }
      setSuccessMessage(null);  
    }
  };
  

  if (loading) return <p>Đang tải dữ liệu...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      {isTeaching? (
        <div>
        <ChildHeader nameHeader={"Thành viên"} />
        <div className='container-paricipants'>
          <div>
            {formError && <p className="error-message">{formError}</p>}
            {successMessage && <p className="success-message">{successMessage}</p>}
          </div>
          <h3>Thêm thành viên</h3>
          <div className="add-participant-form">
            <input
              type="text"
              value={newParticipant.username}
              onChange={(e) => setNewParticipant({ ...newParticipant, username: e.target.value })}
              placeholder="Tên người dùng"
            />
            <select
              value={newParticipant.role}
              onChange={(e) => setNewParticipant({ ...newParticipant, role: e.target.value })}
            >
              <option value="student">Học sinh</option>
              <option value="teacher">Giáo viên</option>
            </select>
            <button onClick={handleAdd}>Thêm</button>
          </div>
    
    
          <h2>Danh sách thành viên</h2>
    
      {/* Bảng giáo viên */}
      <h3>Giáo viên</h3>
      <table border="1" cellPadding="10" cellSpacing="0">
        <thead>
          <tr>
            <th>Tên người dùng</th>
            <th>Xóa</th>
          </tr>
        </thead>
        <tbody>
          {teachers.length > 0 ? (
            teachers.map((teacher) => (
              <tr key={teacher.username}>
                <td>{teacher.username}</td>
                <td>
                  <button
                    onClick={() => handleRemove(teacher.username, 'teacher')}
                    className="remove-button"
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="2">Không có giáo viên nào.</td>
            </tr>
          )}
        </tbody>
      </table>
    
      {/* Bảng học sinh */}
      <h3>Học sinh</h3>
      <table border="1" cellPadding="10" cellSpacing="0">
        <thead>
          <tr>
            <th>Tên người dùng</th>
            <th>Xóa</th>
          </tr>
        </thead>
        <tbody>
          {students.length > 0 ? (
            students.map((student) => (
              <tr key={student.username}>
                <td>{student.username}</td>
                <td>
                  <button
                    onClick={() => handleRemove(student.username, 'student')}
                    className="remove-button"
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="2">Không có học sinh nào.</td>
            </tr>
          )}
        </tbody>
      </table>
        </div>
      </div>
      ):(
        <div>
        <ChildHeader nameHeader={"Thành viên"} />
        <div className='container-paricipants'>

    
          <h2>Danh sách thành viên</h2>
    
      {/* Bảng giáo viên */}
      <h3>Giáo viên</h3>
      <table border="1" cellPadding="10" cellSpacing="0">
        <thead>
          <tr>
            <th>Tên người dùng</th>
          </tr>
        </thead>
        <tbody>
          {teachers.length > 0 ? (
            teachers.map((teacher) => (
              <tr key={teacher.username}>
                <td>{teacher.username}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="2">Không có giáo viên nào.</td>
            </tr>
          )}
        </tbody>
      </table>
    
      {/* Bảng học sinh */}
      <h3>Học sinh</h3>
      <table border="1" cellPadding="10" cellSpacing="0">
        <thead>
          <tr>
            <th>Tên người dùng</th>
          </tr>
        </thead>
        <tbody>
          {students.length > 0 ? (
            students.map((student) => (
              <tr key={student.username}>
                <td>{student.username}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="2">Không có học sinh nào.</td>
            </tr>
          )}
        </tbody>
      </table>
        </div>
      </div>

      )}
    </div>
    
  );
};

export default Participants;
