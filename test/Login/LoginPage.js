import React from "react";
import './LoginPage.css';

const LoginPage = () => {
    return (
        <div className="page">
            <div className="image-block"></div>
            <div className="login-block">
                <div className="email-login">
                    <label>Email</label>
                    <input type="email" placeholder="Enter your email" />
                </div>
                <div className="password-login">
                    <label>Password</label>
                    <input type="password" placeholder="Enter your password" />
                </div>
                <div className="login-button primary">Login</div>
                <div className="login-button secondary">Forgot Password?</div>
            </div>
        </div>
    );
};

export default LoginPage;