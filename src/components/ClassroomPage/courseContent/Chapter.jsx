import React from "react";
import styles from "./CourseContent.module.css";
import LessonItem from "./LessonItem";
import MaterialItem from "./MaterialItem";

const Chapter = ({ number, lessons, materials }) => {
  const chapterClass = `${styles.chapterHeader} ${
    number === 2 ? styles.chapterTwo : number === 3 ? styles.chapterThree : ""
  }`;

  return (
    <>
      <div className={chapterClass}>Chương {number}</div>
      {lessons.map((lesson, index) => (
        <LessonItem key={`lesson-${index}`} title={lesson} />
      ))}
      {materials?.map((material, index) => (
        <MaterialItem key={`material-${index}`} title={material} />
      ))}
    </>
  );
};

export default Chapter;
