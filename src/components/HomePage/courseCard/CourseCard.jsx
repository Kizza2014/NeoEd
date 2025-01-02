import React from "react";
import { useNavigate } from "react-router-dom";  // Import useNavigate hook
import styles from "./CourseCard.module.css";
import { ResourceItem } from "./ResourceItem";

const resources = [
  {
    icon: "https://cdn.builder.io/api/v1/image/assets/TEMP/6d378fdc-5e66-4c54-924d-5dbc8fcf6e7d?placeholderIfAbsent=true&apiKey=2705284951c44eab8fe0922f72983ece",
    text: "Học liệu",
  },
  {
    icon: "https://cdn.builder.io/api/v1/image/assets/TEMP/e2b68746-cac0-434d-8fa3-c198db8956dc?placeholderIfAbsent=true&apiKey=2705284951c44eab8fe0922f72983ece",
    text: "Bài tập",
  },
];

export const CourseCard = ({ courseDetails }) => {
  const { courseTitle, courseId, courseSchedule, instructorInfo, locationInfo } = courseDetails;
  const navigate = useNavigate();  // Initialize navigate function

  const handleClick = () => {
    // Navigate to the Classroom page with the courseTitle as the URL
    navigate(`/Classroom/${courseId}`);
  };

  return (
    <div className={styles.courseContainer} onClick={handleClick} role="button" tabIndex="0">
      <div className={styles.courseInfo}>
        <div className={styles.courseTitle}>{courseTitle}</div>
        <div className={styles.courseSchedule}>{courseSchedule}</div>
        <div className={styles.instructorInfo}>{instructorInfo}</div>
        <div className={styles.locationInfo}>{locationInfo}</div>
      </div>
      <img
        loading="lazy"
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/fba375969cee0ce427e2682ed05d5ccd12cc75079ea455b693a99941ac1025a3?placeholderIfAbsent=true&apiKey=2705284951c44eab8fe0922f72983ece"
        className={styles.divider}
        alt=""
      />
      <div className={styles.resourcesContainer}>
        {resources.map((resource, index) => (
          <ResourceItem key={index} icon={resource.icon} text={resource.text} />
        ))}
      </div>
    </div>
  );
};
