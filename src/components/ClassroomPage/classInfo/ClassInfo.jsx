import React, { useState, useEffect } from "react";
import { ClassInfoRow } from "./ClassInfoRow";
import styles from "./ClassInfo.module.css";
import axios from "axios";
import { PuffLoader } from "react-spinners";
import { useParams } from 'react-router-dom';

export function ClassInfo() {
  const { classId } = useParams();
  const [classDetails, setClassDetails] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [isTeacher, setIsTeacher] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionId, setSessionId] = useState();
  const [checked, setChecked] = useState(false);

  const handleCheckIn = async () => {
    try {
      await axios.post(
        `http://localhost:8000/checkin/student-checkin`,
        null,
        {
          params: {
            session_id: sessionId,
            student_id: sessionStorage.getItem("user_id"),
          },
        }
      );
      setChecked(true);
    } catch (err) {
      console.error("Error during check-in:", err);
      setError("Failed to perform check-in.");
    }
  };

  useEffect(() => {
    const fetchClassInfo = async () => {
      try {
        // Fetch participants in the background
        axios
          .get(`http://localhost:8000/classroom/${classId}/participant/all`)
          .then((participantsResponse) => {
            const students = participantsResponse.data.students || [];
            const teacherIds = participantsResponse.data.teachers.map(teacher => teacher.user_id) || [];
            sessionStorage.setItem("num_students", students.length);
            setParticipants(students);
            console.log("Teachers Id: ", teacherIds)
            console.log("Is teacher?: ",teacherIds.includes(sessionStorage.getItem('user_id')));
            setIsTeacher(teacherIds.includes(sessionStorage.getItem('user_id')));
          })
          .catch((err) => {
            console.error("Error fetching participants:", err);
            setError("Failed to fetch participants.");
          });

        // Fetch class details and session info
        const response = await axios.get(
          `http://localhost:8000/classroom/${classId}/detail`
        );
        const checkInResponse = await axios.get(
          `http://localhost:8000/session/current`,
          { params: { class_id: classId } }
        );

        const data = response.data;
        const adaptedDetails = [
          { label: "Tên lớp", value: data.class_name },
          { label: "Mã lớp", value: data.subject_name },
          { label: "Giáo viên", value: data.owner_fullname },
          { label: "Phòng học", value: "Chưa xác định" },
        ];
        setClassDetails(adaptedDetails);

        if (checkInResponse.data.session_id) {
          setSessionId(checkInResponse.data.session_id);
        }
      } catch (err) {
        console.error("Error fetching class information:", err);
        setError("Failed to fetch class information.");
      } finally {
        setLoading(false);
      }
    };

    if (classId) {
      fetchClassInfo();
    }
  }, [classId]);

  if (error) {
    return (
      <div style={{ display: "flex", padding: "30px" }}>
        {error}
      </div>
    );
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.infoCard}>
          <PuffLoader color="#36d7b7" />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.infoCard}>
        <div className={styles.title}>Thông tin lớp học</div>
        {classDetails.map((detail, index) => (
          <ClassInfoRow key={index} label={detail.label} value={detail.value} />
        ))}
        {/* <div className={styles.curriculum}>Giáo trình</div> */}
        <div className={styles.participants}>
          {sessionId && !isTeacher && (
            <button
              className={styles.checkInButton}
              onClick={handleCheckIn}
              disabled={checked}
            >
              {checked ? "Đã điểm danh" : "Điểm danh"}
            </button>
          )}
        </div>



      </div>
    </div>
  );
}
