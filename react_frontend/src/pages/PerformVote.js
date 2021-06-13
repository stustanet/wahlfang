import React from "react";
import {useHistory, useParams} from "react-router-dom";
import Layout from "../components/Layout";
import {useFormik} from "formik";
import {useRecoilValue} from "recoil";
import {electionById} from "../state";
import {performVote} from "../api";

export default function PerformVote() {
    const {id} = useParams();
    const election = useRecoilValue(electionById(parseInt(id)));
    const history = useHistory();
    // TODO: handle 404

    const optionString = election.voter_self_apply ? "applicant" : "option";
    const options = election.disable_abstention ? ['accept', 'reject'] : ['abstention', 'accept', 'reject'];

    const validate = values => {
        const errors = {};
        for (const val of Object.entries(values)) {
            if (val[1] === null) {
                errors[val[0]] = 'Must select an option';
            }
        }

        return errors;
    }

    const formik = useFormik({
        initialValues: Object.fromEntries(election.applications.map(application => [application.id, null])),
        validate,
        onSubmit: values => {
            performVote(election, values)
                .then(result => {
                    // TODO
                    history.push("/");
                })
                .catch(err => {

                })
        }
    })

    const numYesVotes = Object.values(formik.values).reduce((acc, curr) => acc + (curr === 'accept' ? 1 : 0), 0);

    const selectAllYes = () => {

    }

    return (
        <Layout title="Vote!">
            <div className="card shadow">
                <div className="card-body">
                    {!election.can_vote ? (
                        <div>
                            <span>Already voted</span>
                        </div>
                    ) : (
                        <form onSubmit={formik.handleSubmit}>
                            <div className="form-group">
                                <h4 className="mb-0">{election.title}</h4>
                                <small className="text-muted">Voting Period: {election.application_due_date}
                                    - {election.end_date} (UTC {election.end_date})</small>
                            </div>
                            <hr/>
                            <div className="card">
                                <h5 className="card-header">Instruction</h5>
                                <div className="card-body">
                                    {election.max_votes_yes > 1 ? (
                                        <span>You may give up to {election.max_votes_yes} YES votes.</span>
                                    ) : ""}
                                    <div>
                                        The display order of
                                        the {optionString}s is randomized.<br/>
                                        Your vote is anonymous.
                                    </div>
                                </div>
                            </div>
                            {election.max_votes_yes > 1 && election.max_votes_yes <= election.applications.length ? (
                                <div className="mt-3 d-flex justify-content-end">
                                    <button type="button" className="btn btn-success"
                                            onClick={selectAllYes}>
                                        Select YES for all {election.applications.length} applicants
                                    </button>
                                </div>
                            ) : ""}
                            <table className="table table-sm">
                                <thead className="thead-light">
                                <tr>
                                    <th>{optionString}</th>
                                    {!election.disable_abstention ? (
                                        <th className="text-center">Abstention</th>
                                    ) : ""}
                                    <th className="text-center text-success">YES</th>
                                    <th className="text-center text-muted">NO</th>
                                </tr>
                                </thead>
                                <tbody>
                                {election.applications.map(application => (
                                    <tr>
                                        <td className="applicant">
                                            <div className="row no-gutters">
                                                {application.avatar ? (
                                                    <div className="col-3">
                                                        <img src={application.avatar.url}
                                                             className="card-img" alt="applicant"/>
                                                    </div>
                                                ) : ""}
                                                <div className="col-9">
                                                    <div className="card-body">
                                                        <h6 className="card-title">{application.display_name}</h6>
                                                        <p className="card-text">{application.text}</p>
                                                    </div>
                                                </div>
                                                {formik.touched[application.id] && formik.errors[application.id] ? <span
                                                    className="text-danger">{formik.errors[application.id]}</span> : null}
                                            </div>
                                        </td>
                                        {options.map(option => (
                                            <td className="text-center"><label className="radio">
                                                <input
                                                    type="radio"
                                                    name={application.id}
                                                    onChange={formik.handleChange}
                                                    onBlur={formik.handleBlur}
                                                    value={option}/>
                                            </label></td>
                                        ))}
                                    </tr>
                                ))}
                                </tbody>
                                <tfoot>
                                <tr>
                                    <td/>
                                    <td/>
                                    <td className="text-center">
                                                <span
                                                    className="badge rounded-pill bg-secondary">{election.max_votes_yes - numYesVotes} remaining</span>
                                    </td>
                                    <td/>
                                </tr>
                                </tfoot>
                            </table>
                            <hr/>
                            <div className="d-grid mt-2">
                                <button type="submit" className="btn btn-primary">Submit</button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </Layout>
    )
}