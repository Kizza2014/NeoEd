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
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClassInfo = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/classroom/${classId}/detail`);
        const participantsResponse = await axios.get(`http://localhost:8000/classroom/${classId}/participant/all`);
        const data = response.data;
        const adaptedDetails = [
          { label: "Tên lớp", value: data.class_name },    
          { label: "Mã lớp", value: data.subject_name },  
          { label: "Giáo viên", value: data.owner },     
          { label: "Phòng học", value: "Chưa xác định" }
        ];

        setClassDetails(adaptedDetails);
        setParticipants(participantsResponse.data);

      } catch (err) {
        console.error("Error fetching class information:", err);
        setError("Failed to fetch class information");
      } finally {
        setLoading(false); 
      }
    };

    if (classId) {
      fetchClassInfo();
    }
  }, [classId]);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.infoCard}>
          <PuffLoader color="#36d7b7"/>
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
        <div className={styles.curriculum}>Giáo trình</div>
        <div className={styles.participants}>
          <div className={styles.title}>Danh sách học viên</div>
          {participants.length > 0 ? (
            <ul className={styles.participantList}>
              {participants.map((participant, index) => (
                <li key={index} className={styles.participant}>
                  {participant}
                </li>
              ))}
            </ul>
          ) : (
            <p>Chưa có học viên.</p>
          )}
        </div>
      </div>
    </div>
  );
}

