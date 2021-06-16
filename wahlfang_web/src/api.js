import {stateCounter} from "./state";

export const apiURL = (process.env.REACT_APP_SERVER_URL || 'http://localhost:8000') + '/api/v1';

export const routes = {
    login: "/auth/code/token/",
    refreshToken: "/auth/token/refresh/",
    verifyToken: "/auth/token/verify/",
    voterInfo: "/vote/voter_info/",
    electionList: "/vote/elections/",
}

export async function makeRequest(url = '', type = '',data = null,  headers = {'Content-Type': 'application/json'}) {
    let request = {
        method: type,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: headers,
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
    };
    if (data !== null) {
        request.body = JSON.stringify(data);
    }

    return await fetch(apiURL + url, request);
}

export async function makeAuthenticatedRequest(url = '',  type = '', data = null) {
    let token = loadToken();
    if (!isTokenValid(token.access)) {
        token = await refreshToken();
    }
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.access}`,
    }

    return await makeRequest(url, type, data, headers);
}


export const getJWTPayload = (token) => {
    const decoded = token.split('.')[1];
    return JSON.parse(atob(decoded));
}

export const isTokenValid = (token) => {
    const tokenPayload = getJWTPayload(token);
    return new Date(tokenPayload.exp * 1000) >= new Date()
}

export const loadToken = () => {
    return JSON.parse(localStorage.getItem("token"));
}

export const refreshToken = async () => {
    const response = await makeRequest(routes.refreshToken, 'POST', {
        refresh: loadToken().refresh
    })

    if (response.status < 300) {
        const token = await response.json();
        localStorage.setItem("token", JSON.stringify(token));
        return token;
    } else {
        // TODO: error
    }
}

export const login = async (code) => {
    localStorage.removeItem("token");
    const response = await makeRequest(routes.login, 'POST', {access_code: code});

    if (response.status < 300) {
        const token = await response.json();
        localStorage.setItem("token", JSON.stringify(token));
        return token;
    } else {
        throw Error("error logging in")
    }
}

export const logout = async () => {
    stateCounter.counter++;
    localStorage.removeItem("token");
    return true;
}

export const fetchVoterInfo = async () => {
    const response = await makeAuthenticatedRequest(routes.voterInfo, 'GET');
    return await response.json();
}

export const fetchElections = async () => {
    const response = await makeAuthenticatedRequest(routes.electionList, 'GET');
    return await response.json();
}

export const performVote = async (election, vote) => {
    const response = await makeAuthenticatedRequest(`/vote/elections/${election.id}/perform_vote/`, 'POST', vote);

    if (response.status === 204) {
        return true;
    } else {
        throw Error(await response.json())
    }
}

export const updateApplication = async (election, application) => {
    const response = await makeAuthenticatedRequest(`/vote/elections/${election.id}/application/`, 'POST', application);

    if (response.status === 200) {
        return true;
    } else {
        throw Error(await response.json())
    }
}

export const deleteApplication = async (election) => {
    const response = await makeAuthenticatedRequest(`/vote/elections/${election.id}/application/`, 'DELETE');

    if (response.status === 204) {
        return true;
    } else {
        throw Error()
    }
}
