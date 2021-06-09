import {Redirect, useHistory, useParams} from "react-router-dom";
import {useRecoilValue} from "recoil";
import {electionById} from "../state";
import {Formik} from "formik";
import Layout from "../components/Layout";
import React from "react";
import {updateApplication} from "../api";


export default function Application() {
    const {id} = useParams();
    const election = useRecoilValue(electionById(parseInt(id)));
    const history = useHistory();


    if (!election) { // TODO: handle 404 properly
        return <Redirect to="/"/>
    }

    const handleSubmit = (values) => {
        updateApplication(election, values)
            .then(result => {
                history.push("/") ;
            })
            .catch(err => {

            })
    }

    return (
        <Layout title="application">
            <div className="row justify-content-center">
                <div className="col-lg-6 col-xs-12">
                    <div className="card shadow">
                        <div className="card-body">
                            <Formik initialValues={{
                                display_name: !election.voter_application ? "" : election.voter_application.display_name,
                                email: !election.voter_application ? "" : election.voter_application.email,
                                text: !election.voter_application ? "" : election.voter_application.text,
                            }} onSubmit={handleSubmit}>
                                {({
                                      values,
                                      errors,
                                      touched,
                                      handleChange,
                                      handleBlur,
                                      handleSubmit,
                                      isSubmitting
                                  }) => (
                                    <form onSubmit={handleSubmit}>
                                        <div className="form-group">
                                            {election.voter_application ? (
                                                <h4>Edit Application</h4>
                                            ) : (
                                                <h4>New Application</h4>
                                            )}
                                        </div>
                                        <hr/>
                                        <h5 className="card-title">Display Name</h5>
                                        <div className="form-row">
                                            <div className="form-group col-md-12 mb-0">
                                                <input type="text"
                                                       className="form-control"
                                                       name="display_name"
                                                       onChange={handleChange}
                                                       onBlur={handleBlur}
                                                       value={values.display_name}
                                                       required={true}/>
                                                {errors.display_name && touched.display_name && errors.display_name}
                                            </div>
                                        </div>
                                        <hr/>

                                        <h5 className="card-title">
                                            <span>Contact E-Mail Address</span>
                                            <span className="badge bg-secondary">Optional</span>
                                        </h5>
                                        <span className="form-text text-muted mb-2">The e-mail address will not be visible to voters.</span>
                                        <div className="form-row">
                                            <div className="form-group col-md-12 mb-0">
                                                <input type="email"
                                                       className="form-control"
                                                       name="email"
                                                       onChange={handleChange}
                                                       onBlur={handleBlur}
                                                       value={values.email}
                                                       required={false}/>
                                                {errors.email && touched.email && errors.email}
                                            </div>
                                        </div>
                                        <hr/>

                                        <h5 className="card-title">
                                            <span>Application Info</span>
                                            <span className="badge bg-secondary">Optional</span></h5>
                                        <span><strong>This information is visible to voters!</strong></span><br/>
                                        <span className="form-text text-muted mb-2">Add a short description of the applicant.</span>
                                        <div className="form-row">
                                            <div className="form-group col-md-12 mb-0">
                                            <textarea
                                                cols="40" rows="2" maxLength="250"
                                                className="form-control"
                                                name="text"
                                                onChange={handleChange}
                                                onBlur={handleBlur}
                                                value={values.text}
                                                required={false}/>
                                                {errors.text && touched.text && errors.text}
                                            </div>
                                        </div>
                                        <hr/>

                                        {/*<span*/}
                                        {/*    className="form-text text-muted mt-4 mb-2">Add a photo of the applicant.</span>*/}
                                        {/*{{form.avatar}}*/}
                                        <div className="d-grid mt-2">
                                            <button type="submit" className="btn btn-primary btn-block">Submit</button>
                                        </div>
                                    </form>
                                )}
                            </Formik>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}