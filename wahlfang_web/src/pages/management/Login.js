import React from "react";
import Layout from "../../components/Layout";
import {Redirect, useHistory} from "react-router-dom";
import {Formik} from "formik";
import {loginManager} from "../../api/management";
import {useRecoilState} from "recoil";
import {isManagerAuthenticated} from "../../state/management";


export default function LoginManager() {
    const [authenticated, setAuthenticated] = useRecoilState(isManagerAuthenticated);
    const history = useHistory();

    const handleSubmit = (values, {setSubmitting}) => {
        loginManager(values.username, values.password)
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
        <Layout title="loginManager">
            <div className="card o-hidden border-0 shadow-lg my-5">
                <div className="card-body">
                    <div className="p-5">
                        <Formik initialValues={{username: "", password: ""}} onSubmit={handleSubmit}>
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
                                        <h4>Management Login</h4>
                                    </div>
                                    <div className="form-group">
                                        <input type="text" className="form-control form-control-user"
                                               id="id_username"
                                               name="username"
                                               placeholder="Username"
                                               autoFocus={true}
                                               onChange={handleChange}
                                               onBlur={handleBlur}
                                               value={values.username}
                                               required={true}/>
                                           {errors.username && touched.username && errors.username}
                                    </div>
                                    <div className="form-group">
                                        <input type="password" className="form-control form-control-user"
                                               id="id_password"
                                               name="password"
                                               placeholder="Password"
                                               autoFocus={true}
                                               onChange={handleChange}
                                               onBlur={handleBlur}
                                               value={values.password}
                                               required={true}/>
                                           {errors.password && touched.password && errors.password}
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