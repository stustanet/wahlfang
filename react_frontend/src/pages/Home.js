import React from "react";
import Layout from "../components/Layout";
import {useRecoilValue} from "recoil";
import {openElections, publishedElections, unpublishedElections, upcomingElections, voterInfo} from "../state";
import Election from "../components/Election";

export default function Home() {
    const voter = useRecoilValue(voterInfo);
    const upcoming = useRecoilValue(upcomingElections);
    const unpublished = useRecoilValue(unpublishedElections);
    const open = useRecoilValue(openElections);
    const published = useRecoilValue(publishedElections);

    return (
        <Layout>
            <div className="row justify-content-center">
                <div className="col-12">
                    <div className="card bg-dark text-light shadow mb-2 py-2">
                        <div className="card-body">
                            <h4 className="text-center d-inline">{voter.session.title}</h4>
                            {voter.session.meeting_link !== null ? (
                                <div><small>Meeting at <a
                                    href={voter.session.meeting_link}>{voter.session.meeting_link}</a></small>
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
                                        <Election key={election.id} election={election}/>
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
                                        <Election key={election.id} election={election}/>
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
                                        <Election key={election.id} election={election}/>
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
                                        <Election key={election.id} election={election}/>
                                    ))}
                                </div>
                            </div>
                        ) : ""}
                    </div>
                </div>
            </div>
        </Layout>
    )
}