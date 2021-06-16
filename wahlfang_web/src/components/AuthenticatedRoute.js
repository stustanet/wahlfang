import React from "react";
import {useRecoilValue} from "recoil";
import {isAuthenticated} from "../state";
import {Redirect} from "react-router-dom";

export default function AuthenticatedRoute({authFallback = "/code", children}) {
    const authenticated = useRecoilValue(isAuthenticated);

    return (
        <>
            {!authenticated ? <Redirect to={authFallback}/> : children}
        </>
    )
}