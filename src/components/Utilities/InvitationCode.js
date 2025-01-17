import React, { useEffect, useState } from "react";
import { Link, useLocation, useParams } from 'react-router-dom';
import "./Breadcrumbs.css"
import axios from "axios";
import { BarLoader } from "react-spinners";
import './InvitationCode.css'
function InvitationCode () {
    const [inviteCode, setInviteCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState();
    const token = sessionStorage.getItem('access_token');
    const {classId} = useParams();
    useEffect(() => {
        const fetchCode = async () => {
            try {
                setLoading(true);
                console.log(classId);
                console.log(token);
                const response = await axios.get(
                    `http://127.0.0.1:8000/classroom/${classId}/invitation-code`,
                    {
                      params: {
                        token,
                      },
                    }
                  );
                const data = response.data;
                setInviteCode(data);
                console.log(data);
            } catch (error) {
                console.error("Error fetching assignment details:", error);
                setError("An error occurred: " + error.message + " " + error.code);
            } finally {
                setLoading(false);
            }
        };

        fetchCode();
    }, [classId]);

    if (loading) {
        return (
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
            <BarLoader color="#36d7b7" />
          </div>
        );
      }
    
      if (error) {
        return (
          <div style={{ display: "flex", padding: "30px" }}>
            {error}
          </div>
        );
      }

      return (
        <div className="join-code">
            <h3>Mã tham gia lớp học: </h3>
            <h3 className="code"> {inviteCode}</h3>
        </div>
      );
}

export default InvitationCode;