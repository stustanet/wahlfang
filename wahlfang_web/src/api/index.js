export const apiURL = (process.env.REACT_APP_SERVER_URL || 'http://127.0.0.1:8000') + '/api/v1';

export const voteAPIRoutes = {
    login: "/auth/code/token/",
    refreshToken: "/auth/token/refresh/",
    verifyToken: "/auth/token/verify/",
    voterInfo: "/vote/voter_info/",
    electionList: "/vote/elections/",
}

export async function makeRequest(url = '', type = '', data = null, headers = {'Content-Type': 'application/json'}) {
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

export async function makeAuthenticatedVoterRequest(url = '', type = '', data = null) {
    let token = loadVoterToken();
    if (!isTokenValid(token.access)) {
        token = await refreshVoterToken();
    }
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.access}`,
    }

    return await makeRequest(url, type, data, headers);
}


export const getJWTPayload = (token) => {
    console.log(token)
    const decoded = token.split('.')[1];
    return JSON.parse(atob(decoded));
}

export const isTokenValid = (token) => {
    const tokenPayload = getJWTPayload(token);
    console.log(new Date(tokenPayload.exp * 1000) >= new Date())
    return new Date(tokenPayload.exp * 1000) >= new Date()
}

export const loadVoterToken = () => {
    return JSON.parse(localStorage.getItem("voterToken"));
}

export const refreshVoterToken = async () => {
    const response = await makeRequest(voteAPIRoutes.refreshToken, 'POST', {
        refresh: loadVoterToken().refresh
    })

    if (response.status < 300) {
        const token = await response.json();
        localStorage.setItem("voterToken", JSON.stringify(token));
        return token;
    } else {
        // TODO: error
    }
}

export const loginVoter = async (code) => {
    localStorage.removeItem("voterToken");
    const response = await makeRequest(voteAPIRoutes.login, 'POST', {access_code: code});

    if (response.status < 300) {
        const token = await response.json();
        localStorage.setItem("voterToken", JSON.stringify(token));
        return token;
    } else {
        throw Error("error logging in")
    }
}

export const logoutVoter = async () => {
    localStorage.removeItem("voterToken");
    return true;
}

export const fetchSpectatorInfo = async (uuid) => {
    const response = await makeRequest(`/vote/spectator/${uuid}/`, 'GET');
    if (response.status === 200) {
        return response.json();
    } else {
        throw Error("could not fetch spectator view")
    }
}

export const fetchVoterInfo = async () => {
    const response = await makeAuthenticatedVoterRequest(voteAPIRoutes.voterInfo, 'GET');
    return await response.json();
}

export const fetchElections = async () => {
    const response = await makeAuthenticatedVoterRequest(voteAPIRoutes.electionList, 'GET');
    return await response.json();
}

export const performVote = async (election, vote) => {
    const response = await makeAuthenticatedVoterRequest(`/vote/elections/${election.id}/perform_vote/`, 'POST', vote);

    if (response.status === 204) {
        return true;
    } else {
        throw Error(await response.json())
    }
}

export const updateApplication = async (election, application) => {
    const response = await makeAuthenticatedVoterRequest(`/vote/elections/${election.id}/application/`, 'POST', application);

    if (response.status === 200) {
        return true;
    } else {
        throw Error(await response.json())
    }
}

export const deleteApplication = async (election) => {
    const response = await makeAuthenticatedVoterRequest(`/vote/elections/${election.id}/application/`, 'DELETE');

    if (response.status === 204) {
        return true;
    } else {
        throw Error()
    }
}
