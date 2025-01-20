import React, {useState} from "react";
import "./LoginPage.css";
import logo from './logo.png';
import facebook from './facebook.png'
import google from './google.png'
import { useNavigate } from 'react-router-dom';
import axios from "axios";
import { FadeLoader } from "react-spinners";
import useWindowSize from "../Teacher/teacher_home/SizeContext";
import { FaFacebook, FaGoogle } from "react-icons/fa";


function LoginButton({userName,password}) {
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const handleLogin = async () => {
        setLoading(true);
        console.log({ username: userName, password: password });
    
        try {

            const loginResponse = await axios.post('http://127.0.0.1:8000/login', {
                username: userName,
                password: password,
            });
    
            const info = loginResponse.data;
            console.log('Login successful:', info);
    

            sessionStorage.setItem('access_token', info.access_token);
            sessionStorage.setItem('isTeaching', false);
            localStorage.setItem('user_id', info.user_id);
            sessionStorage.setItem('user_id', info.user_id);
            localStorage.setItem('refresh_token', info.refresh_token);
    

            const userDetailsResponse = await axios.get(`http://127.0.0.1:8000/user/${info.user_id}/detail`);
            localStorage.setItem('username', userDetailsResponse.data.fullname);
            console.log('User details fetched successfully:', userDetailsResponse.data);

            setLoading(false);
            navigate('/c');
        } catch (error) {
            console.error('Error during login or fetching user details:', error);
            alert('Login failed: Check your email or password');
            setLoading(false);
        }
    };
      

    if (loading) {
        return(
            <>
                <button 
                className="login-button" 
                onClick={handleLogin}
            >
                    Đăng nhập
                </button>
                <div className="login-loading">
                    <FadeLoader
                    color="#ffb800"
                    height={50}
                    margin={60}
                    radius={3}
                    width={15}
                    />
                </div>
            </>
        )
    }

    return (
        <button 
            className="login-button" 
            onClick={handleLogin}
        >
            Đăng nhập
        </button>
    );
}

function LoginPage() {
    const [userName, setUserName] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate()
    const {width} = useWindowSize();
    const handleEmailChange = (event) => {
        setUserName(event.target.value);
    };

    const handlePasswordChange = (event) => {
        setPassword(event.target.value);
    };
    console.log({ username: userName, password: password })
    return (
        <div>
            {width >600? (
            <div>
                <div className="container">
            <div className="left-div"></div>
            <div className="right-div">
                <img src={logo} className="logo" alt="Description" loading="lazy"/>
                <div className="form-container">
                    <div className="input-container">
                        <label htmlFor="email">Tên đăng nhập</label>
                        <input
                            value={userName}
                            onChange={handleEmailChange}
                            type="email"
                            className="input"
                            required
                        />
                    </div>

                    <div className="input-container">
                        <label htmlFor="password">Mật khẩu</label>
                        <input
                            value={password}
                            onChange={handlePasswordChange}
                            type="password"
                            className="input"
                            required
                        />
                    </div>
                </div>
                <div className='check-box'>
                    <label>
                        <input type="checkbox" className='remember-pass' />
                        <span >Ghi nhớ đăng nhập</span>
                    </label>
                    <button type="button" className='forgot-password'>
                        Quên mật khảu?
                    </button>
                </div>
                <LoginButton userName={userName} password={password} />
                <div className="divider">
                    <span className="line"></span>
                    <span className="dividerText">Hoặc</span>
                    <span className="line"></span>
                </div>
                <div className="registerPrompt">
                    Chưa có tài khoản?
                    <button
                    className="registerLink"
                    onClick={() => navigate('/s')} 
                    >
                    Đăng ký ngay
                    </button>
                </div>
                <div className="social-login">
                    <div 
                        className="social-button google" 
                        onClick={() => window.open("https://accounts.google.com", "_blank")}
                    >
                    <FaGoogle size={25}/>
                    <div>
                        Đăng nhập bằng Google
                    </div>
                        
                    </div>
                    <div 
                        className="social-button facebook" 
                        onClick={() => window.open("https://www.facebook.com", "_blank")}
                    >
                      <FaFacebook size={25}/>
                      <div>
                        Đăng nhập bằng Facebook
                      </div>

                    </div>
                </div>
            </div>
        </div>
            </div>
            ):(
                // <div className="content-m">
                //     <img src={logo} className="logo-m" alt="Description" loading="lazy" />
                //     <div className="form-container-m">
                //     <div className="input-container-m">
                //         <label htmlFor="email">Địa chỉ email</label>
                //         <input
                //         value={userName}
                //         onChange={handleEmailChange}
                //         type="email"
                //         className="input"
                //         required
                //         />
                //     </div>

                //     <div className="input-container-m">
                //         <label htmlFor="password">Mật khẩu</label>
                //         <input
                //         value={password}
                //         onChange={handlePasswordChange}
                //         type="password"
                //         className="input"
                //         required
                //         />
                //     </div>

                //     <div className="check-box-m">
                //         <label>
                //         <input type="checkbox" className="remember-pass-m" />
                //         <span>Ghi nhớ đăng nhập</span>
                //         </label>
                //         <button type="button" className="forgot-password-m">
                //         Quên mật khẩu?
                //         </button>
                //     </div>
                //         <LoginButton
                //         className = "button-login"
                //         userName={userName}
                //         password={password}
                //     />
                //     <div className="registerPrompt-m">
                //         Chưa có tài khoản?
                //         <button type="button" className="registerLink">
                //         Đăng ký ngay
                //         </button>
                //     </div>
                //     </div>
                // </div>
                <div className="content-m">
                <img src={logo} className="logo-m" alt="Description" loading="lazy"/>
                <div className="form-container">
                    <div className="input-container">
                        <label htmlFor="email">Tên đăng nhập</label>
                        <input
                            value={userName}
                            onChange={handleEmailChange}
                            type="email"
                            className="input"
                            required
                        />
                    </div>

                    <div className="input-container">
                        <label htmlFor="password">Mật khẩu</label>
                        <input
                            value={password}
                            onChange={handlePasswordChange}
                            type="password"
                            className="input"
                            required
                        />
                    </div>
                </div>
                <div className='check-box'>
                    <label>
                        <input type="checkbox" className='remember-pass' />
                        <span >Ghi nhớ đăng nhập</span>
                    </label>
                    <button type="button" className='forgot-password'>
                        Quên mật khảu?
                    </button>
                </div>
                <LoginButton userName={userName} password={password} />
                {/* <div className="divider">
                    <span className="line"></span>
                    <span className="dividerText">Hoặc</span>
                    <span className="line"></span>
                </div> */}
                <div className="registerPrompt">
                    Chưa có tài khoản?
                    <button type="button" className="registerLink">
                        Đăng kí ngay
                    </button>
                </div>
                <div className="social-login">
                    <div 
                        className="social-button google" 
                        onClick={() => window.open("https://accounts.google.com", "_blank")}
                    >
                    <FaGoogle size={25}/>
                    <div>
                        Đăng nhập bằng Google
                    </div>
                        
                    </div>
                    <div 
                        className="social-button facebook" 
                        onClick={() => window.open("https://www.facebook.com", "_blank")}
                    >
                      <FaFacebook size={25}/>
                      <div>
                        Đăng nhập bằng Facebook
                      </div>

                    </div>
                </div>
            </div>

            )}
        </div>
    );
}

export default LoginPage;
