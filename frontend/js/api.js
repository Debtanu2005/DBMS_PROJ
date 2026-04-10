const BASE_URL = "http://127.0.0.1:8000";

export function getToken() {
    return localStorage.getItem("token");
}

export function setToken(token) {
    localStorage.setItem("token", token);
}

export function getHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + getToken()
    };
}