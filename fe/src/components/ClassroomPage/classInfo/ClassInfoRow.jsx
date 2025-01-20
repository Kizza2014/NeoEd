import React from "react";
import styles from "./ClassInfoRow.module.css";

export function ClassInfoRow({ label, value }) {
  return (
    <div className={styles.row}>
      <div className={styles.label}>{label}</div>
      <div className={styles.value}>{value}</div>
    </div>
  );
}
