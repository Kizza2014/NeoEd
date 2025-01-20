import React from "react";
import styles from "./CourseContent.module.css";

const LessonItem = ({ title }) => (
  <div className={styles.lessonItem}>{title}</div>
);

export default LessonItem;
