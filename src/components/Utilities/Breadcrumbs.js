import React, { useEffect, useState } from "react";
import { Link, useLocation, useParams } from 'react-router-dom';
import "./Breadcrumbs.css";
import axios from "axios";
import { BarLoader } from "react-spinners";

const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);
  const { classId, postId, assignmentId } = useParams();

  const [className, setClassName] = useState(null);
  const [postName, setPostName] = useState(null);
  const [assignmentName, setAssignmentName] = useState(null);

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const isTeaching = sessionStorage.getItem("isTeaching") === "true";

  const breadcrumbMapping = {
    c: "Classroom",
    a: "Assignments",
    p: "Posts",
    n: "Notifications",
    r: "Requests",
  };

  useEffect(() => {
    const fetchClassName = async () => {
      try {
        if (classId) {
          const response = await axios.get(`http://localhost:8000/classroom/${classId}/detail`, {
            params: {
              token: sessionStorage.getItem("access_token"),
            },
          });
          setClassName(response.data.class_name);
        }

        if (postId) {
          const response = await axios.get(`http://localhost:8000/classroom/${classId}/post/${postId}/detail`, {
            params: {
              token: sessionStorage.getItem("access_token"),
            },
          });
          setPostName(response.data.title);
        }

        if (assignmentId) {
          const response = await axios.get(`http://localhost:8000/classroom/${classId}/assignment/${assignmentId}/detail`, {
            params: {
              token: sessionStorage.getItem("access_token"),
            },
          });
          setAssignmentName(response.data.title);
        }
      } catch (err) {
        setError("Failed to fetch class name");
      } finally {
        setLoading(false);
      }
    };

    fetchClassName();
  }, [assignmentId, classId, postId]);

  if (loading) {
    return <BarLoader color="#36d7b7" width="100%" />;
  }

  let breadcrumbPathnames = pathnames.filter((value) => value !== "t");

  return (
    <nav aria-label="breadcrumb">
      <ol className="breadcrumb">
        {error && <li className="breadcrumb-item text-danger">{error}</li>}
        {breadcrumbPathnames.map((value, index) => {
          let to = `/${breadcrumbPathnames.slice(0, index + 1).join("/")}`;
          
          if (
            isTeaching &&
            index > 0 && // Ensure this is not the root breadcrumb
            breadcrumbPathnames[index - 1] === "c" 
          ) {
            to = to.replace("/c", "/c/t");
          }

          const isLast = index === breadcrumbPathnames.length - 1;

          let displayValue = breadcrumbMapping[value] || value;

          if (index === 1 && className) {
            displayValue = className;
          }

          if (index === 3 && postName) {
            displayValue = postName;
          }

          if (index === 3 && assignmentName) {
            displayValue = assignmentName;
          }

          return isLast ? (
            <li key={to} className="breadcrumb-item active" aria-current="page">
              {displayValue}
            </li>
          ) : (
            <li key={to} className="breadcrumb-item">
              <Link to={to}>{displayValue}</Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
