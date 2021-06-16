import React from "react";
import {useRecoilValue} from "recoil";
import {isVoterAuthenticated} from "../state";
import {Redirect} from "react-router-dom";

export default function AuthenticatedRoute({authFallback = "/code", children}) {
    const authenticated = useRecoilValue(isVoterAuthenticated);
    if (!authenticated) {
        console.log("redirecting to login")
    }

    return (
        <>
            {!authenticated ? <Redirect to={authFallback}/> : children}
        </>
    )
}