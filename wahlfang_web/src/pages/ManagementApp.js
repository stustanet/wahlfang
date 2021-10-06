import React, {Suspense, useEffect, useState} from 'react';
import {Route, Switch, useRouteMatch} from "react-router-dom";
import {useRecoilState} from "recoil";
import {isManagerAuthenticated} from "../state/management";
import Loading from "../components/Loading";
import {isTokenValid} from "../api";
import LoginManager from './management/Login';
import {loadManagerToken, refreshManagerToken} from "../api/management";
import Help from "./management/Help";
import {managementWS} from "../websocket";
import Header from "../components/Header";
import Logout from "./vote/Logout";
import AuthenticatedRoute from "../components/AuthenticatedRoute";


export default function ManagementApp() {
    const [authenticated, setAuthenticated] = useRecoilState(isManagerAuthenticated);
    const [loading, setLoading] = useState(!authenticated);
    const {path} = useRouteMatch();

    useEffect(() => {
        const authToken = loadManagerToken();
        if (authToken && isTokenValid(authToken.access)) {
            setAuthenticated(true);
            setLoading(false);
            managementWS.initWs();
            console.log("found valid access token");
        } else if (authToken && isTokenValid(authToken.refresh)) {
            console.log("found valid refresh token");
            refreshManagerToken()
                .then(() => {
                    setAuthenticated(true);
                    setLoading(false);
                    managementWS.initWs();
                })
                .catch(() => {
                    setLoading(false);
                })
        } else {
            setLoading(false);
        }
    }, [setLoading, setAuthenticated])

    return (
        <>
            {loading ? <Loading/> : (
                <div id="content">
                    <Header/>
                    <Switch>
                        <Route exact path={`${path}/login`}>
                            <Suspense fallback={<Loading/>}>
                                <LoginManager/>
                            </Suspense>
                        </Route>
                        <Route exact path={path}>
                            <Help/>
                        </Route>
                        <Route exact path={`${path}/help`}>
                            <Help/>
                        </Route>
                        <AuthenticatedRoute>
                            <Route exact path="/logout">
                                <Suspense fallback={<Loading/>}>
                                    <Logout/>
                                </Suspense>
                            </Route>
                        </AuthenticatedRoute>
                    </Switch>
                </div>
            )}
        </>
    );
}