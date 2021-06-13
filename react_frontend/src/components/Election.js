import React from "react";
import moment from "moment";
import {Link} from "react-router-dom";
import {deleteApplication} from "../api";

export default function Election({election}) {

    const removeApplication = () => {
        deleteApplication(election);
    }

    return (
        <div className="card mb-2">
            <div className="card-body">
                <h4 className="d-flex justify-content-between">
                    <span>{election.title}</span>
                    {(election.start_date === null || new Date(election.start_date) > new Date()) && election.voters_self_apply ? (
                        <span>
                            <Link className="btn btn-dark btn-sm"
                                  to={`/election/${election.id}/application`}>{!election.voter_application ? "Apply" : "Edit Application"}</Link>
                            {election.voter_application ? (
                                <button className="btn btn-danger btn-sm" onClick={removeApplication}>Delete
                                    Application</button>
                            ) : null}
                        </span>
                    ) : null}
                </h4>
                {election.end_date ? (
                    <>
                        <small className="text-muted">Voting Period: {moment(election.start_date).format('llll')}
                            - {moment(election.end_date).format('llll')}</small>
                    </>
                ) : null}
                <hr/>
                <div className="list-group mt-3">
                    {election.can_vote ? (
                        <Link className="btn btn-primary" to={`/election/${election.id}/vote`}>Vote Now!</Link>
                    ) : new Date(election.end_date) <= new Date() && election.result_published === '1' ? (
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
                    ) : election.start_date === null || new Date(election.start_date) > new Date() ? (
                        <button className="btn btn-outline-dark disabled">
                            {election.start_date !== null ?
                                `Voting starts ${moment(election.start_date).format('llll')}`
                                : "Wait for the admin to start the election"}
                        </button>
                    ) : (
                        <div className="alert alert-success" role="alert">
                            <h4 className="alert-heading">Thank You For Your Vote!</h4>
                            <hr/>
                            <p className="mb-0">This election will end {moment(election.end_date).format('llll')}</p>
                        </div>
                    )}
                    {!election.start_date || new Date(election.start_date) > new Date() ? (
                        <>
                            <hr/>
                            <h5 className="mb-0 mt-4">{election.voters_self_apply ? "Applicants" : "Options"}</h5>
                            {election.max_votes_yes > 1 ? (
                                <small className="text-muted">Up to {election.max_votes_yes} applicants will be
                                    elected.</small>
                            ) : null}
                            {election.applications.length === 0 ? (
                                <span>No {election.voters_self_apply ? "applicants" : "options"} to vote so far ...</span>
                            ) : (
                                <div className="mt-3">
                                    <div className="row row-cols-1 row-cols-md-2 vote-list">
                                        {election.applications.map(application => (
                                            <div className="col mb-2" key={application.id}>
                                                <div className="applicant">
                                                    {application.avatar ? (
                                                        <img src={application.avatar.url} className="applicant-picture"
                                                             alt="applicant"/>
                                                        // <img src="{% static 'img/blank_avatar.png' %}" className="applicant-picture"
                                                        //      alt = "applicant-picture" />
                                                    ) : null}
                                                    <h6>{application.display_name}</h6>
                                                    <p className="description">{application.text}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    ) : null}

                </div>
            </div>
        </div>
    )
}