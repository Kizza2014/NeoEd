import './ClassroomPage.css';
import React from "react";
import logo from '../Utilities/logined_logo.png';
import TopBar from '../Utilities/Top_bar';
import { NavLink, useParams } from 'react-router-dom';
import { Outlet } from 'react-router-dom';

function ClassroomPage() {
  const { classId } = useParams();
  return (
    <div className="container">
      <div className="slide">
        <img src={logo} className="logo" alt="Description" loading="lazy" />
        <div className="button-list">
          <NavLink
            to={`/Classroom/${classId}`}
            className={({ isActive }) => (isActive ? "active_class_link" : "")}
            end
          >
            Thông tin lớp học
          </NavLink>
          <NavLink
            to={`/Classroom/${classId}/notifications`}
            className={({ isActive }) => (isActive ? "active_class_link" : "")}
          >
            Thông báo
          </NavLink>
          <NavLink
            to={`/Classroom/${classId}/posts`}
            className={({ isActive }) => (isActive ? "active_class_link" : "")}
          >
            Học liệu
          </NavLink>
          <NavLink
            to={`/Classroom/${classId}/assignment`}
            className={({ isActive }) => (isActive ? "active_class_link" : "")}
          >
            Bài tập
          </NavLink>
          <NavLink
            to={`/Classroom/${classId}/requests`}
            className={({ isActive }) => (isActive ? "active_class_link" : "")}
          >
            Gửi yêu cầu cho giáo viên
          </NavLink>
          <NavLink
            to="/Classroom"
            className={({ isActive }) => (isActive ? "active_class_link" : "")}
            end
          >
            Thoát lớp học
          </NavLink>
        </div>
      </div>
      <div className="content-div">
        <TopBar />
        <Outlet />
      </div>
    </div>
  );
}

export default ClassroomPage;

// const classDetails = [
//     { label: "Tên lớp", value: "Cơ sở dữ liệu" },
//     { label: "Mã lớp", value: "8dfas5a" },
//     { label: "Giáo viên", value: "Nguyễn văn A" },
//     { label: "Phòng học", value: "503T5" },
// ];

// const files = [
//     "Assignment1.ipynb",
//     "Solution1.pdf",
//     "Readme.txt",
//     "Readme.txt",
// ];

// const exerciseData = {
//     exercise_name: "Bài tập tuần 1",
//     date: new Date(),
//     exercise_note: "Các em nộp file .ipynb nhé, sau thời gian trên sẽ không nộp được bài nữa, những ai chưa nộp bài sẽ coi như nghỉ không phép.",
//     files: files,
// };

// const notifications = [
//     {
//         author: "Admin",
//         date: new Date(),
//         content: "Your assignment has been graded.",
//     },
//     {
//         author: "System",
//         date: new Date(),
//         content: "The server will be down for maintenance at midnight.",
//     },
//     {
//         author: "Teacher",
//         date: new Date(),
//         content: "Class has been rescheduled to tomorrow at 9 AM.",
//     },
// ];

// function ClassroomPage() {
//     const location = useLocation();
//     const { classId } = useParams();
//     const [activeIndex, setActiveIndex] = useState(0);

//     // const buttons = [
//     //     { label: 'Thông tin lớp học', path: `/Classroom/${classId}/info` },
//     //     { label: 'Thông báo', path: `/Classroom/${classId}/notifications` },
//     //     { label: 'Học liệu', path: `/Classroom/${classId}/content` },
//     //     { label: 'Bài tập', path: `/Classroom/${classId}/assigment` },
//     //     { label: 'Gửi yêu cầu cho giáo viên', path: `/Classroom/${classId}/requests` },
//     //     { label: 'Thoát lớp học', path: `/Classroom/` },
//     // ];

//     // return (
//     //     <div className="container">
//     //         <div className="slide">
//     //             <img src={logo} className="logo" alt="Description" loading="lazy" />
//     //             <div className="button-list">
//     //                 {buttons.map((button, index) => (
//     //                     <Link to={button.path} key={index} className={`button ${location.pathname === button.path ? 'active' : ''}`}>
//     //                         {button.label}
//     //                     </Link>
//     //                 ))}
//     //             </div>
//     //         </div>
//     //     </div>
//     // );

//     const buttons = [
//         'Thông tin lớp học',
//         'Thông báo',
//         'Học liệu',
//         'Bài tập',
//         'Gửi yêu cầu cho giáo viên',
//         'Thoát lớp học',
//     ];

//     const handleClick = (index) => {
//         setActiveIndex(index);
//     };

//     const renderContent = () => {
//         switch (activeIndex) {
//             case 0:
//                 return <ClassInfo classId={classId} />;
//             case 1:
//                 return <Notifications notifications={notifications} />;
//             case 2:
//                 return <CourseContent />;
//             case 3:
//                 return <Exercise exerciseData={exerciseData} />;
//             case 4:
//                 return <Request />;
//             case 5:
//                 return <div>Đã thoát lớp học.</div>;
//             default:
//                 return null;
//         }
//     };

//     return (
//         <div className="container">
//             <div className="slide">
//                 <img src={logo} className="logo" alt="Description" loading="lazy" />
//                 <div className="button-list">
//                     {buttons.map((button, index) => (
//                         <button
//                             key={index}
//                             className={`button ${activeIndex === index ? 'active' : ''}`}
//                             onClick={() => handleClick(index)}
//                         >
//                             {button}
//                         </button>
//                     ))}
//                 </div>
//             </div>
//             <div className="content-div">
//                 <TopBar />
//                 {renderContent()}
//             </div>
//         </div>
//     );
// }

