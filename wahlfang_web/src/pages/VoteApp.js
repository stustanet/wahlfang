import React, {Suspense, useEffect, useState} from 'react';
import {Route, Switch} from "react-router-dom";
import {useRecoilState} from "recoil";

import Login from './vote/Login';
import Logout from './vote/Logout';
import Home from './vote/Home';
import {isVoterAuthenticated} from "../state";
import Loading from "../components/Loading";
import {isTokenValid, loadVoterToken, refreshVoterToken} from "../api";
import AuthenticatedRoute from "../components/AuthenticatedRoute";
import Help from "./vote/Help";
import PerformVote from "./vote/PerformVote";
import {voterWS} from "../websocket";
import Application from "./vote/Application";
import Header from "../components/Header";


export default function VoteApp() {
    const [authenticated, setAuthenticated] = useRecoilState(isVoterAuthenticated);
    const [loading, setLoading] = useState(!authenticated);

    useEffect(() => {
        if (loading && !authenticated) {
            const authToken = loadVoterToken();
            if (authToken && isTokenValid(authToken.access)) {
                setAuthenticated(true);
                setLoading(false);
                voterWS.initWs();
                console.log("found valid access token");
            } else if (authToken && isTokenValid(authToken.refresh)) {
                console.log("found valid refresh token");
                refreshVoterToken()
                    .then(() => {
                        setAuthenticated(true);
                        setLoading(false);
                        voterWS.initWs();
                    })
                    .catch(() => {
                        setLoading(false);
                    })
            } else {
                setLoading(false);
            }
        }
    }, [loading, setLoading, authenticated, setAuthenticated])

    console.log("vote app loading:", loading);

    return (
        <>
            {loading ? <Loading/> : (
                <div id="content">
                    <Header/>
                    <Switch>
                        <Route exact path="/code">
                            <Suspense fallback={<Loading/>}>
                                <Login/>
                            </Suspense>
                        </Route>
                        <Route exact path="/help">
                            <Help/>
                        </Route>
                        <AuthenticatedRoute>
                            <Route exact path="/logout">
                                <Suspense fallback={<Loading/>}>
                                    <Logout/>
                                </Suspense>
                            </Route>
                            <Route exact path="/election/:id/vote">
                                <Suspense fallback={<Loading/>}>
                                    <PerformVote/>
                                </Suspense>
                            </Route>
                            <Route exact path="/election/:id/application">
                                <Suspense fallback={<Loading/>}>
                                    <Application/>
                                </Suspense>
                            </Route>
                            <Route exact path="/">
                                <Suspense fallback={<Loading/>}>
                                    <Home/>
                                </Suspense>
                            </Route>
                        </AuthenticatedRoute>
                    </Switch>
                </div>
            )}
        </>
    );
}
