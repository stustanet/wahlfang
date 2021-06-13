import React, {Suspense, useEffect, useState} from 'react';
import {BrowserRouter as Router, Route, Switch} from "react-router-dom";
import Login from './pages/Login';
import Logout from './pages/Logout';

import About from './pages/About';
import Home from './pages/Home';
import {useRecoilState} from "recoil";
import {isAuthenticated} from "./state";
import Loading from "./components/Loading";
import {isTokenValid, loadToken, refreshToken} from "./api";
import AuthenticatedRoute from "./components/AuthenticatedRoute";
import Help from "./pages/Help";
import PerformVote from "./pages/PerformVote";
import {ws} from "./websocket";
import Application from "./pages/Application";


function App() {
    const [authenticated, setAuthenticated] = useRecoilState(isAuthenticated);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (loading && !authenticated) {
            const authToken = loadToken();
            if (authToken && isTokenValid(authToken.access)) {
                setAuthenticated(true);
                setLoading(false);
                ws.initWs();
                console.log("found valid access token");
            } else if (authToken && isTokenValid(authToken.refresh)) {
                console.log("found valid refresh token");
                refreshToken()
                    .then(() => {
                        setAuthenticated(true);
                        setLoading(false);
                        ws.initWs();
                    })
                    .catch(() => {
                        setLoading(false);
                    })
            } else {
                setLoading(false);
            }
        }
    }, [loading, setLoading, authenticated, setAuthenticated])

    return (
        <>
            {loading ? <Loading/> : (
                <Router>
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
                            <Route exact path="/about">
                                <About/>
                            </Route>
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
                        <Route path="*">404</Route>
                    </Switch>
                </Router>
            )}
        </>
    );
}

export default App;