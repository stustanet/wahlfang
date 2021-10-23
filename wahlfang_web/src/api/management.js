import {makeRequest, isTokenValid, makeAuthenticatedVoterRequest, voteAPIRoutes} from "./index";

export const managementAPIRoutes = {
    login: "/auth/token/",
    refreshToken: "/auth/token/refresh/",
    verifyToken: "/auth/token/verify/",
    createSession: "/management/add-session",
}

// Help functions

export const loadManagerToken = () => {
    return JSON.parse(localStorage.getItem("managerToken"));
}

export async function makeAuthenticatedManagerRequest(url = '', type = '', data = null) {
    let token = loadManagerToken();
    if (!isTokenValid(token.access)) {
        token = await refreshManagerToken();
    }
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.access}`,
    }

    return await makeRequest(url, type, data, headers);
}


// Auth api calls

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
    localStorage.removeItem("managerToken");
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

// API calls

export const createSession = async (form_values) => {
    const response = await makeAuthenticatedManagerRequest(managementAPIRoutes.createSession, 'POST', form_values);
    if (response.status === 201) {
        return true;
    } else {
        throw Error(await response.json())
    }
}

export const fetchSessions = async () => {
    const response = await makeAuthenticatedManagerRequest(managementAPIRoutes.createSession, 'GET');
    console.log(response)
    return await response.json();
}