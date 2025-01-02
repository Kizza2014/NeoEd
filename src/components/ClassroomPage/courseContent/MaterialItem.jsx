import React from "react";
import styles from "./CourseContent.module.css";

const MaterialItem = ({ title }) => (
  <div className={styles.materialItem}>{title}</div>
);

export default MaterialItem;
