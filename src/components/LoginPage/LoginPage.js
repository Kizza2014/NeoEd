import React from "react";
import styles from "./LoginPage.css";
import logo from './logo.png';
import facebook from './facebook.png'
import google from './google.png'
import { useNavigate } from 'react-router-dom';

function LoginButton() {
    const navigate = useNavigate();
    return (
        <button 
            className="login-button" 
            onClick={() => navigate('/Classroom')}
            >
            Login
        </button>
    );
}

function LoginPage() {
    return (
        <div className="container">
            <div className="left-div"></div>
            <div className="right-div">
                <img src={logo} className="logo" alt="Description" loading="lazy" />
                <div className="form-container">
                    <div className="input-container">
                        <label htmlFor="email">Địa chỉ email</label>
                        <input type="email" className="input" required/>
                    </div>

                    <div className="input-container">
                        <label htmlFor="password">Mật khẩu</label>
                        <input type="password" className="input" required />
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
                <LoginButton/>
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
