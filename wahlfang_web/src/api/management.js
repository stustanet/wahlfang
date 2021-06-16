import {makeRequest} from "./index";

export const managementAPIRoutes = {
    login: "/auth/code/token/",
    refreshToken: "/auth/token/refresh/",
    verifyToken: "/auth/token/verify/",
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
