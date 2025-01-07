import React, { useEffect, useState } from "react";
import { Link, useLocation, useParams } from 'react-router-dom';
import "./Breadcrumbs.css"
import axios from "axios";
import { BarLoader } from "react-spinners";

const Breadcrumbs = () => {
  const location = useLocation(); 
  const pathnames = location.pathname.split('/').filter((x) => x);
  const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);
  const { classId } = useParams();
  const [className, setClassName] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const breadcrumbMapping = {
    c: "Classroom",
    a: "Assigments",
    p: "Posts",
    n: "Notifications",
    r: "Requestss"
  };

  useEffect(() => {
    const fetchClassName = async () => {
      try {
        if (classId) {
          const response = await axios.get(`http://localhost:8000/classroom/${classId}/detail`);
          setClassName(response.data.class_name);
        }
      } catch (err) {
        setError("Failed to fetch class name");
      } finally {
        setLoading(false);
      }
    };
    
    fetchClassName();
  }, [classId]);

    if (loading) {
      return <BarLoader color="#36d7b7" width="100%" />;
    }
    return (
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          {error && <li className="breadcrumb-item text-danger">{Error}</li>}
          {pathnames.map((value, index) => {
            const to = `/${pathnames.slice(0, index + 1).join('/')}`;
            const isLast = index === pathnames.length - 1;
  
            // Map the key from breadcrumbMapping or use the original value
            let displayValue = breadcrumbMapping[value] || value;
  
            // Replace the `classId` with `className` if applicable
            if (index === 1 && className) {
              displayValue = className;
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
