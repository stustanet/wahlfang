import React, {useEffect} from "react";
import {Redirect} from "react-router-dom";
import {logout} from "../api";
import Layout from "../components/Layout";
import {useRecoilState} from "recoil";
import {isAuthenticated} from "../state";
import Loading from "../components/Loading";

export default function Logout() {
    const [authenticated, setAuthenticated] = useRecoilState(isAuthenticated);

    useEffect(() => {
        logout().then(result => {
            // TODO: somehow reset the state
            setAuthenticated(false);
        });
    })

    return (
        <Layout title="logout">
            {authenticated ? <Loading/> : <Redirect to="/code"/>}
        </Layout>
    );
}