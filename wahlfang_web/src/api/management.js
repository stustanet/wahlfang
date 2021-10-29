import {makeRequest, isTokenValid, makeAuthenticatedVoterRequest, voteAPIRoutes} from "./index";

export const managementAPIRoutes = {
    login: "/auth/token/",
    refreshToken: "/auth/token/refresh/",
    verifyToken: "/auth/token/verify/",
    manageSessions: "/manager/add-session",
    manageElections: "/manager/election"

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

// sessions

export const createSession = async (form_values) => {
    const response = await makeAuthenticatedManagerRequest(managementAPIRoutes.manageSessions, 'POST', form_values);
    if (response.status === 201) {
        return true;
    } else {
        throw Error(await response.json())
    }
}

export const fetchSessions = async () => {
    const response = await makeAuthenticatedManagerRequest(managementAPIRoutes.manageSessions, 'GET');
    return await response.json()
}

export const deleteSession = async (pk) => {
    const url = `${managementAPIRoutes.manageSessions}?pk=${pk}`
    console.log(url)
    const response = await makeAuthenticatedManagerRequest(url, 'DELETE')
    console.log(response)
    if (response.status === 204) {
        return true;
    } else {
        throw new Error(await response.json())
    }
}

// Elections

export const fetchElections = async (sessionId) => {
    const url = `${managementAPIRoutes.manageElections}`
    const response = await makeAuthenticatedManagerRequest(url, 'GET');
    return await response.json()
}


export const deleteElection = async (pk) => {
    const url = `${managementAPIRoutes.manageElections}?pk=${pk}`
    const response = await makeAuthenticatedManagerRequest(url, 'DELETE')
    console.log(response)
    if (response.status === 204) {
        return true;
    } else {
        throw new Error(await response.json())
    }
}

