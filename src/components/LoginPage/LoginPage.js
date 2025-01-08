import React, {useState} from "react";
import styles from "./LoginPage.css";
import logo from './logo.png';
import facebook from './facebook.png'
import google from './google.png'
import { useNavigate } from 'react-router-dom';
import axios from "axios";
import { FadeLoader } from "react-spinners";

function LoginButton({userName,password}) {
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const handleLogin = () => {
        setLoading(true);
        axios.post(
            'http://localhost:8000/login', 
            { username: 'user', password: 'password' },
        )
        .then(response => {
            var info = response.data;
            console.log('Login successful:', response.data);
            sessionStorage.setItem('access_token', info.access_token);
            sessionStorage.setItem('isTeaching', false);
            localStorage.setItem('user_id', info.user_id);
            localStorage.setItem('refresh_token', info.refresh_token);
            setLoading(false);
            navigate('/c');
        })
        .catch(error => {
            alert(`Login failed: Check your email or password`);
            setLoading(false);
        });
    };

    if (loading) {
        return(
            <>
                <button 
                className="login-button" 
                onClick={handleLogin}
            >
                    Login
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
            Login
        </button>
    );
}

function LoginPage() {
    const [userName, setUserName] = useState("scottdavis");
    const [password, setPassword] = useState("1");
    const handleEmailChange = (event) => {
        setUserName(event.target.value);
    };

    const handlePasswordChange = (event) => {
        setPassword(event.target.value);
    };

    return (
        <div className="container">
            <div className="left-div"></div>
            <div className="right-div">
                <img src={logo} className="logo" alt="Description" loading="lazy"/>
                <div className="form-container">
                    <div className="input-container">
                        <label htmlFor="email">Địa chỉ email</label>
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
                    <button type="button" className="registerLink">
                        Đăng kí ngay
                    </button>
                </div>
                <div className="social-login">
                    <div 
                        className="social-button google" 
                        onClick={() => window.open("https://accounts.google.com", "_blank")}
                    >
                    <img 
                        src={google}
                        alt="Google logo" 
                        className="social-logo" 
                    />
                        Đăng nhập bằng Google
                    </div>
                    <div 
                        className="social-button facebook" 
                        onClick={() => window.open("https://www.facebook.com", "_blank")}
                    >
                    <img 
                        src={facebook}
                        alt="Facebook logo" 
                        className="social-logo" 
                    />
                        Đăng nhập bằng Facebook
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
