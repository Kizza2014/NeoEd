import React from "react";
import styles from "./CourseCard.module.css";

export const ResourceItem = ({ icon, text }) => {
  return (
    <div className={styles.resourceItem}>
      <img loading="lazy" src={icon} className={styles.resourceIcon} alt="" />
      <div>{text}</div>
    </div>
  );
};
