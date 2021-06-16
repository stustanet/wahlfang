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
            setAuthenticated(false);
            // TODO: this is a very hacky way of reloading the whole app such that the recoil app state is reset.
            // TODO: find a saner way of resetting the recoil state without having to force reload the whole page.
            window.location.assign('/');
        });
    })

    return (
        <Layout title="logout">
            {authenticated ? <Loading/> : <Redirect to="/code"/>}
        </Layout>
    );
}