import React, {Suspense, useState} from 'react';
import {BrowserRouter as Router, Switch, Route} from "react-router-dom";
import Loading from "./components/Loading";
import VoteApp from "./pages/VoteApp";
import ManagementApp from "./pages/ManagementApp";
import SpectatorView from "./pages/SpectatorView";
import About from "./pages/About";


function App() {
    const [loading, setLoading] = useState(false);

    return (
        <>
            {loading ? <Loading/> : (
                <Router>
                    <Switch>
                        <Route exact path="/about">
                            <About/>
                        </Route>
                        <Route exact path="/spectator/:uuid">
                            <Suspense fallback={<Loading/>}>
                                <SpectatorView/>
                            </Suspense>
                        </Route>
                        <Route path="/management">
                            <Suspense fallback={<Loading/>}>
                                <ManagementApp/>
                            </Suspense>
                        </Route>
                        <Route path="/">
                            <Suspense fallback={<Loading/>}>
                                <VoteApp/>
                            </Suspense>
                        </Route>
                        <Route path="*">404</Route>
                    </Switch>
                </Router>
            )}
        </>
    );
}

export default App;