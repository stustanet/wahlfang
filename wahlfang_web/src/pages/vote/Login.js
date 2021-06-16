import React from "react";
import Layout from "../../components/Layout";
import {Redirect, useHistory} from "react-router-dom";
import {Formik} from "formik";
import {loginVoter} from "../../api";
import {useRecoilState} from "recoil";
import {isVoterAuthenticated} from "../../state";

export default function Login() {
    const [authenticated, setAuthenticated] = useRecoilState(isVoterAuthenticated);
    const history = useHistory();

    const handleSubmit = (values, {setSubmitting}) => {
        loginVoter(values.accessCode)
            .then(res => {
                setAuthenticated(true);
                setSubmitting(false);
                history.push("/");
            })
            .catch(err => {
                setSubmitting(false);
            })
    }

    if (authenticated) {
        return <Redirect to="/"/>
    }

    return (
        <Layout title="login">
            <div className="card o-hidden border-0 shadow-lg my-5">
                <div className="card-body">
                    <div className="p-5">
                        <Formik initialValues={{accessCode: ""}} onSubmit={handleSubmit}>
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
                                        <label>Login with your access code received by e-mail</label>
                                    </div>
                                    <div className="mt-3 form-group">
                                        <input type="text"
                                               className="form-control form-control-user text-center"
                                               name="accessCode"
                                               placeholder="Access Code"
                                               autoFocus={true}
                                               onChange={handleChange}
                                               onBlur={handleBlur}
                                               value={values.accessCode}
                                               required={true}/>
                                        {errors.accessCode && touched.accessCode && errors.accessCode}
                                    </div>
                                    <div className="d-grid mt-2">
                                        <button type="submit" className="btn btn-primary">Login</button>
                                    </div>
                                </form>
                            )}
                        </Formik>
                    </div>
                </div>
            </div>
        </Layout>
    )
}