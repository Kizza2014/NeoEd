import React from 'react';
import Slider from './components/HomePage/Slider.js';
import LoginPage from './components/LoginPage/LoginPage.js';
import { ClassInfo } from './components/ClassroomPage/classInfo/ClassInfo.jsx';
import Notification_page from './components/ClassroomPage/notification/Notifications.js';
import { CourseContent } from './components/ClassroomPage/courseContent/CourseContent.jsx';
import Request from './components/ClassroomPage/Requests/Request.js';
import Exercise from './components/ClassroomPage/Exercise/Exercise.js';
import ClassroomPage from './components/ClassroomPage/ClassroomPage.js';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import TeacherHomePage from './components/Teacher/teacher_home/TeacherHomePage.js';

const files = [
  "Assignment1.ipynb",
  "Solution1.pdf",
  "Readme.txt",
  "Readme.txt",
];

const exerciseData = {
  exercise_name: "Bài tập tuần 1",
  date: new Date(),
  exercise_note: "Các em nộp file .ipynb nhé, sau thời gian trên sẽ không nộp được bài nữa, những ai chưa nộp bài sẽ coi như nghỉ không phép.",
  files: files,
};

const notifications = [
  {
      author: "Admin",
      date: new Date(),
      content: "Your assignment has been graded.",
  },
  {
      author: "System",
      date: new Date(),
      content: "The server will be down for maintenance at midnight.",
  },
  {
      author: "Teacher",
      date: new Date(),
      content: "Class has been rescheduled to tomorrow at 9 AM.",
  },
];

export default function MyApp() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/Classroom" element={<TeacherHomePage />} />
      <Route path="/Classroom/:classId" element={<ClassroomPage />}>
        <Route path="" element={<ClassInfo/>} />
        <Route path="notifications" element={<Notification_page files={files} />} />
        <Route path="posts" element={<CourseContent />} />
        <Route path="assignment" element={<Exercise files={files} />} />
        <Route path="requests" element={<Request />} />
      </Route>
    </Routes>
  </BrowserRouter>

  );
}
