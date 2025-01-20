import React from 'react';
import Slider from './components/HomePage/Slider.js';
import LoginPage from './components/LoginPage/LoginPage.js';
import { ClassInfo } from './components/ClassroomPage/classInfo/ClassInfo.jsx';
import Notification_page from './components/ClassroomPage/notification/Notifications.js';
import CheckinList from './components/ClassroomPage/Attendance/CheckinList/Checkin.js';
import Exercise from './components/ClassroomPage/Exercise/Exercise.js';
import ClassroomPage from './components/ClassroomPage/ClassroomPage.js';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import TeacherHomePage from './components/Teacher/teacher_home/TeacherHomePage.js';
import TeacherClassroomPage from './components/Teacher/TeacherClassroomPage.js';
import Exercise_description from './components/ClassroomPage/Exercise/ExerciseDetail/ExerciseDetail.js';
import Exercise_scoring from './components/ClassroomPage/Exercise/ExerciseDetail/ExerciseScoring.js';
import Post_description from './components/ClassroomPage/posts/PostDetails/PostDetail.js';
import UserProfile from './components/HomePage/userinfo/UserProfileWithButton.js';
import Register from './components/LoginPage/Register/Register'
import Participants from './components/ClassroomPage/Participants/Participants.js'
import Checkin from "./components/ClassroomPage/Attendance/AttendanceCheck/AttendanceCheck.js"
export default function MyApp() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path ="/s" element = {<Register/>}/>
      <Route path="/c" element={<TeacherHomePage />}>
          <Route path="r" element={<CheckinList />} />
      </Route>
      <Route path='/u' element ={<UserProfile/>}/>
      <Route path="/c/t/:classId" element={<ClassroomPage />}>
        <Route path="p/:postId" element={<Post_description />}/>
        <Route path="a" element={<Exercise/>}>
            <Route path=":assignmentId" element={<Exercise_scoring />} />
        </Route>
        <Route path = "pa" element = {<Participants/>}/>
        <Route path="r" element={<CheckinList />}/>
      </Route>
      <Route path="/c/:classId" element={<TeacherClassroomPage />}>
        <Route path="p/:postId" element={<Post_description />}/>
        <Route path="a" element={<Exercise />}>
            <Route path=":assignmentId" element={<Exercise_description />} />
        </Route>
        <Route path = "pa" element = {<Participants/>}/>
        <Route path="r" element={<CheckinList />}/>
      </Route>
    </Routes>
  </BrowserRouter>

  );
}
