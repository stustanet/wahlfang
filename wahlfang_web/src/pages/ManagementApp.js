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
import HeaderManagement from "../components/HeaderManagement";
import Logout from "./management/Logout";
import ManagerAuthenticatedRoute from "../components/ManagerAuthenticatedRoute";
import AddSession from "./management/AddSession"


export default function ManagementApp() {
    const [authenticated, setAuthenticated] = useRecoilState(isManagerAuthenticated);
    const [loading, setLoading] = useState(!authenticated);
    const {path} = useRouteMatch();
    useEffect(() => {
        const authToken = loadManagerToken();
        if (authToken && authToken.access && isTokenValid(authToken.access)) {
            console.log(authToken.access)
            setAuthenticated(true);
            setLoading(false);
            managementWS.initWs();
            console.log("found valid access token");
        } else if (authToken && authToken.refresh && isTokenValid(authToken.refresh)) {
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
                    <HeaderManagement/>
                    <Switch>
                        <Route exact path={path}>
                            <LoginManager/>
                        </Route>
                        <Route exact path={`${path}/login`}>
                            <Suspense fallback={<Loading/>}>
                                <LoginManager/>
                            </Suspense>
                        </Route>
                        <Route exact path={`${path}/help`}>
                            <Help/>
                        </Route>
                        <Route exact path={`${path}/add-session`}>
                            <AddSession/>
                        </Route>
                        <ManagerAuthenticatedRoute>
                         <Route exact path={`${path}/logout`}>
                            <Suspense fallback={<Loading/>}>
                                <Logout/>
                            </Suspense>
                        </Route>
                        </ManagerAuthenticatedRoute>
                    </Switch>
                </div>
            )}
        </>
    );
}
