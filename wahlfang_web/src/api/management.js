import {makeRequest, isTokenValid} from "./index";

export const managementAPIRoutes = {
    login: "/auth/token/",
    refreshToken: "/auth/token/refresh/",
    verifyToken: "/auth/token/verify/",
    createSession: "management/add-session",
}

export const loadManagerToken = () => {
    return JSON.parse(localStorage.getItem("managerToken"));
}

export const refreshManagerToken = async () => {
    const response = await makeRequest(managementAPIRoutes.refreshToken, 'POST', {
        refresh: loadManagerToken().refresh
    })

    if (response.status < 300) {
        const token = await response.json();
        localStorage.setItem("managerToken", JSON.stringify(token));
        return token;
    } else {
        // TODO: error
    }
}

export const loginManager = async (username, password) => {
    console.log(managementAPIRoutes.login)
    const response = await makeRequest(managementAPIRoutes.login, 'POST', {
        username: username,
        password: password
    })
     if (response.status < 300) {
        const token = await response.json();
        localStorage.setItem("managerToken", JSON.stringify(token));
        return token;
    } else {
        throw Error("error logging in")
    }
}

export const logoutManager = async () => {
    localStorage.removeItem("managerToken");
    return true;
}

export const createSession = async (form_values) => {
    const response = await makeRequest(managementAPIRoutes.createSession, 'POST', form_values);
    if (response.status === 204) {
        return true;
    } else {
        throw Error(await response.json())
    }
}