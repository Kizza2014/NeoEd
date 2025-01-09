import React from 'react';
import Slider from './components/HomePage/Slider.js';
import LoginPage from './components/LoginPage/LoginPage.js';
import { ClassInfo } from './components/ClassroomPage/classInfo/ClassInfo.jsx';
import Notification_page from './components/ClassroomPage/notification/Notifications.js';
import Request from './components/ClassroomPage/Requests/Request.js';
import Exercise from './components/ClassroomPage/Exercise/Exercise.js';
import ClassroomPage from './components/ClassroomPage/ClassroomPage.js';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import TeacherHomePage from './components/Teacher/teacher_home/TeacherHomePage.js';
import Exercise_description from './components/ClassroomPage/Exercise/ExerciseDetail/ExerciseDetail.js';
import Post_description from './components/ClassroomPage/posts/PostDetails/PostDetail.js';

const files = [
  "Assignment1.ipynb",
  "Solution1.pdf",
  "Readme.txt",
  "Readme.txt",
];

export default function MyApp() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/c" element={<TeacherHomePage />} />
      <Route path="/c/:classId" element={<ClassroomPage />}>
        <Route path="n" element={<Notification_page files={files} />} />
        <Route path="p/:postId" element={<Post_description />}/>
        <Route path="a" element={<Exercise files={files} />}>
            <Route path=":assignmentId" element={<Exercise_description />} />
        </Route>
        <Route path="r" element={<Request />}/>
      </Route>
    </Routes>
  </BrowserRouter>

  );
}
