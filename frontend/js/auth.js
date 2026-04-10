import { BASE_URL, setToken } from "./api.js";

// REGISTER
export async function registerUser(email, password) {
    const res = await fetch(`${BASE_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email,
            password,
            student_info: {}
        })
    });

    const data = await res.json();
    if (res.ok) {
        setToken(data.access_token);
        alert("Registered successfully!");
        window.location.href = "index.html";
    } else {
        alert(data.detail);
    }
}

// LOGIN
export async function loginUser(email, password) {
    const res = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (res.ok) {
        setToken(data.access_token);
        alert("Login successful!");
        window.location.href = "index.html";
    } else {
        alert(data.detail);
    }
}