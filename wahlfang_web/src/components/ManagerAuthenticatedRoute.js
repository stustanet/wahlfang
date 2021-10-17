import React from "react";
import {useRecoilValue} from "recoil";
import {Redirect} from "react-router-dom";
import {isManagerAuthenticated} from "../state/management"

export default function ManagerAuthenticatedRoute({authFallback = "/management/login", children}) {
    const authenticated = useRecoilValue(isManagerAuthenticated);
    if (!authenticated) {
        console.log("Manager not authenticated. Redirecting to manager login")
    }
    return (
        <>
            {!authenticated ? <Redirect to={authFallback}/> : children}
        </>
    )
}