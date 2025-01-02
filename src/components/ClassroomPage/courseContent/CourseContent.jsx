import React from "react";
import styles from "./CourseContent.module.css";
import Chapter from "./Chapter";

export function CourseContent() {
  const courseData = [
    {
      number: 1,
      lessons: [
        "Bài 1: Mở đầu về cơ sở dữ liệu",
        "Bài 1: Mở đầu về cơ sở dữ liệu",
      ],
      materials: ["Học liệu: Chương I"],
    },
    {
      number: 2,
      lessons: [
        "Bài 1: Mở đầu về cơ sở dữ liệu",
        "Bài 1: Mở đầu về cơ sở dữ liệu",
        "Bài tập : Cơ sở dữ liệu",
      ],
    },
    {
      number: 3,
      lessons: [
        "Bài 1: Mở đầu về cơ sở dữ liệu",
        "Bài 1: Mở đầu về cơ sở dữ liệu",
      ],
      materials: ["Học liệu: Chương I"],
    },
  ];

  return (
    <div className={styles.container}>
      {courseData.map((chapter, index) => (
        <Chapter
          key={`chapter-${index}`}
          number={chapter.number}
          lessons={chapter.lessons}
          materials={chapter.materials}
        />
      ))}
    </div>
  );
}
