import React, {useEffect} from "react";
import {logoutVoter} from "../../api";
import Layout from "../../components/Layout";
import {useSetRecoilState} from "recoil";
import {isVoterAuthenticated} from "../../state";
import Loading from "../../components/Loading";

export default function Logout() {
    const setAuthenticated = useSetRecoilState(isVoterAuthenticated);

    useEffect(() => {
        logoutVoter().then(result => {
            setAuthenticated(false);
            // TODO: this is a very hacky way of reloading the whole app such that the recoil app state is reset.
            // TODO: find a saner way of resetting the recoil state without having to force reload the whole page.
            window.location.assign('/');
        });
    })

    return (
        <Layout title="logout">
            <Loading/>
        </Layout>
    );
}