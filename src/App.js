import React from 'react';
import Slider from './components/HomePage/Slider.js';
import LoginPage from './components/LoginPage/LoginPage.js';
import { ClassInfo } from './components/ClassroomPage/classInfo/ClassInfo.jsx';
import Notifications from './components/ClassroomPage/notification/Notifications.js';
import { CourseContent } from './components/ClassroomPage/courseContent/CourseContent.jsx';
import Request from './components/ClassroomPage/Requests/Request.js';
import Exercise from './components/ClassroomPage/Exercise/Exercise.js';
import ClassroomPage from './components/ClassroomPage/ClassroomPage.js';
import { BrowserRouter, Routes, Route} from 'react-router-dom';

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
      <Route path="/Classroom" element={<Slider />} />
      <Route path="/Classroom/:classId" element={<ClassroomPage />}>
        {/* Define child routes */}
        <Route path="" element={<ClassInfo/>} />
        <Route path="notifications" element={<Notifications notifications={notifications} />} />
        <Route path="content" element={<CourseContent />} />
        <Route path="assignment" element={<Exercise exerciseData={exerciseData} />} />
        <Route path="requests" element={<Request />} />
      </Route>
    </Routes>
  </BrowserRouter>

  );
}
