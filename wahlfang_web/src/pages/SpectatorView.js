import Layout from "../components/Layout";
import React, {useEffect, useState} from "react";
import {useParams} from "react-router-dom";
import {fetchSpectatorInfo} from "../api";
import Loading from "../components/Loading";
import SpectatorElection from "../components/SpectatorElection";
import Header from "../components/Header";


export default function SpectatorView() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState({});

    // TODO: error handling, reloading

    const {uuid} = useParams();

    useEffect(() => {
        fetchSpectatorInfo(uuid)
            .then((result) => {
                setData(result);
                setLoading(false)
            })
            .catch((err) => {
                setError(err.toString());
                setLoading(false);
            })
    }, [uuid, setLoading, setData, setError])

    if (loading || error !== null) {
        return (
            <div id="content">
                <Header/>
                <Layout>
                    {loading ? (
                        <Loading/>
                    ) : (
                        <div className="alert alert-danger">{error}</div>
                    )}
                </Layout>
            </div>
        )
    }

    const elections = data.elections;
    const open = elections.filter((election) => election.start_date !== null && new Date(election.start_date) <= new Date() && (election.end_date === null || new Date(election.end_date) > new Date()));
    const upcoming = elections.filter((election) => election.start_date === null || new Date(election.start_date) > new Date());
    const closed = elections.filter((election) => election.end_date && new Date(election.end_date) <= new Date());
    const unpublished = closed.filter((election) => election.result_published === '0');
    const published = closed.filter((election) => election.result_published === '1');

    return (
        <div id="content">
            <Header/>
            <Layout>
                <div className="card bg-dark text-light shadow mb-2 py-2">
                    <div className="card-body">
                        <h4 className="text-center d-inline">{data.title}</h4>
                        {data.meeting_link !== null ? (
                            <div><small>Meeting at <a
                                href={data.meeting_link}>{data.meeting_link}</a></small>
                            </div>
                        ) : ""}
                    </div>
                </div>
                <div id="electionCard">
                    {open.length > 0 ? (
                        <div className="card shadow mb-2">
                            <div className="card-header">
                                <h4>Open Elections</h4>
                            </div>
                            <div className="card-body">
                                {open.map(election => (
                                    <SpectatorElection key={election.id} election={election}/>
                                ))}
                            </div>
                        </div>
                    ) : ""}
                    {upcoming.length > 0 ? (
                        <div className="card shadow mb-2">
                            <div className="card-header">
                                <h4>Upcoming Elections</h4>
                            </div>
                            <div className="card-body">
                                {upcoming.map(election => (
                                    <SpectatorElection key={election.id} election={election}/>
                                ))}
                            </div>
                        </div>
                    ) : ""}
                    {unpublished.length > 0 ? (
                        <div className="card shadow mb-2">
                            <div className="card-header">
                                <h4>Closed Elections</h4>
                            </div>
                            <div className="card-body">
                                {unpublished.map(election => (
                                    <SpectatorElection key={election.id} election={election}/>
                                ))}
                            </div>
                        </div>
                    ) : ""}
                    {published.length > 0 ? (
                        <div className="card shadow mb-2">
                            <div className="card-header">
                                <h4>Published Results</h4>
                            </div>
                            <div className="card-body">
                                {published.map(election => (
                                    <SpectatorElection key={election.id} election={election}/>
                                ))}
                            </div>
                        </div>
                    ) : ""}
                </div>
            </Layout>
        </div>
    )
}