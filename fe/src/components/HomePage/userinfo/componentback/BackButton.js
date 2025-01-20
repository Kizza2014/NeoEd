import React from "react";
import { useNavigate } from "react-router-dom";

const BackButton = () => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/c');
  };

  return (
    <button
      className="back-button"
      onClick={handleBack}
    >
      Quay lại lớp
    </button>
  );
};

export default BackButton;
