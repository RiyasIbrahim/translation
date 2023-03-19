import React, { useState } from "react";

export const Login = () => {
    const [username, setUsername] = useState('');
    const [pass, setPass] = useState('');
    const [errorMessage, setErrorMessage] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', pass);
        //Authentication
        fetch('http://localhost:8000/wiki/login/', {
        method: 'POST',
        body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data['error']) {
                throw Error(data['error']);
            }
            //Store the token in localStorage
            localStorage.clear();
            localStorage.setItem('wiki-trans-token', data['access']);
            localStorage.setItem('wiki-trans-refresh-token', data['refresh']);
            window.location.href = '/';
        })
        .catch(error => setErrorMessage(error.message))
    }

    //Time out set to 5 sec for showing error messages

    setTimeout(() => {
        setErrorMessage("");
      }, 5000);

    return (
        <div>
            <p>{errorMessage}</p>
            <div className="auth-form-container">
                <h2>Login</h2>
                {/* Form for login */}
                <form className="login-form" onSubmit={handleSubmit}>
                    <label htmlFor="email">username</label>
                    <input value={username} onChange={(e) => setUsername(e.target.value)} type="text" placeholder="username" id="username" name="username" />
                    <label htmlFor="password">password</label>
                    <input value={pass} onChange={(e) => setPass(e.target.value)} type="password" placeholder="********" id="password" name="password" />
                    <button type="submit">Log In</button>
                </form>
                
            </div>
        </div>
    )
}