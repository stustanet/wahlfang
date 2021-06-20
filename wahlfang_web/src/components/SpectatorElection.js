import React from "react";
import moment from "moment";

export default function SpectatorElection({election}) {
    const isOpen = election.start_date !== null && (new Date(election.start_date) <= new Date() && (election.end_date === null || new Date(election.end_date) > new Date()));
    const isClosed = election.end_date !== null && new Date(election.end_date) <= new Date();

    return (
        <div className="card mb-2">
            <div className="card-body">
                <h4 className="d-flex justify-content-between">
                    <span>{election.title}</span>
                </h4>
                {election.end_date ? (
                    <>
                        <small className="text-muted">Voting Period: {moment(election.start_date).format('llll')}
                            - {moment(election.end_date).format('llll')}</small>
                    </>
                ) : null}
                <hr/>
                <div className="list-group mt-3">
                    {isClosed && election.result_published === '1' ? (
                        <div className="alert alert-info" role="alert">
                            <h4 className="alert-heading">Voting Ended:</h4>
                            <hr/>
                            <table className="table table-striped">
                                <thead className="thead-dark">
                                <tr>
                                    <th scope="col">#</th>
                                    <th scope="col">{election.voters_self_apply ? "Applicant" : "Option"}</th>
                                    <th scope="col">Yes</th>
                                    <th scope="col">No</th>
                                    <th scope="col">Abstention</th>
                                </tr>
                                </thead>
                                <tbody>
                                {election.election_summary.map((application, index) => (
                                    <tr key={index}>
                                        <th scope="row">{index + 1}</th>
                                        <td>{application.display_name}</td>
                                        <td>{application.votes_accept}</td>
                                        <td>{application.votes_reject}</td>
                                        <td>{application.votes_abstention}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    ) : !isOpen && !isClosed ? (
                        <button className="btn btn-outline-dark disabled">
                            Election has not started yet.
                        </button>
                    ) : isOpen && !isClosed ? (
                        <button className="btn btn-outline-dark disabled">
                            Election is currently ongoing.
                        </button>
                    ) : (
                        <button className="btn btn-outline-dark disabled">
                            Election is over but results haven't been published yet. Please ask your election manager to
                            do so and refresh the page.
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}