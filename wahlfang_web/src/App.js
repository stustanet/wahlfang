import React, {Suspense, useState} from 'react';
import {BrowserRouter as Router, Switch, Route} from "react-router-dom";
import Loading from "./components/Loading";
import VoteApp from "./pages/VoteApp";
import ManagementApp from "./pages/ManagementApp";
import SpectatorView from "./pages/SpectatorView";
import About from "./pages/About";
import {createBrowserHistory} from 'history';
import {RecoilRoot} from 'recoil';

function App() {
    const [loading, setLoading] = useState(false);
    const historyInstance = createBrowserHistory();

    return (
        <RecoilRoot>
            {loading ? <Loading/> : (
                <Router history={historyInstance}>
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
                        {/*<Route path="/vote" exact={true}>*/}
                        {/*    <Suspense fallback={<Loading/>}>*/}
                        {/*        <VoteApp/>*/}
                        {/*    </Suspense>*/}
                        {/*</Route>*/}
                        <Route path={["/", "/vote"]}>
                            <Suspense fallback={<Loading/>}>
                                <VoteApp/>
                            </Suspense>
                        </Route>
                        {/*<Route>404</Route>*/}
                    </Switch>
                </Router>
            )}
        </RecoilRoot>
    );
}

export default App;