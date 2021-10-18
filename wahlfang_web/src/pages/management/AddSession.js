import React, {useState} from 'react';
// import {useHistory, useParams} from "react-router-dom";
import Layout from "../../components/Layout";
// import {useFormik} from "formik";
// import {useRecoilValue} from "recoil";
// import {createSession} from "../../api/management";
import {toggleAddSession} from "../../state/management"
import { Formik, Form, Field } from 'formik';
import {useRecoilState} from "recoil";
import Collapse from 'react-bootstrap/Collapse';


export default function AddSession() {
    const [toggle, setToggle] = useState(false);


    const handleSubmit = (values, {setSubmitting}) => {
        console.log("Adding session submit")
    }

    // const formik = useFormik({
    //     onSubmit: values => {
    //         createSession(values)
    //             .then(result => {
    //                 history.push('/')
    //             })
    //             .catch(err => {
    //                 // TODO
    //             })
    //     }
    //
    // })
    // Render Prop

    const handleToggle = () => {
        setToggle(!toggle)
    }

    const Basic = () => (
      <div className="p-5">
        <Formik
          initialValues={{ title: '', start_date: '', meeting_link: ''}}
          onSubmit={handleSubmit}
        >
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
                        <label>Create Session</label>
                    </div>
                    <div className="mt-3 form-group">
                        <input type="text"
                               className="form-control form-control-user text-center"
                               name="sessionTitle"
                               placeholder="Session's Title"
                               autoFocus={true}
                               onChange={handleChange}
                               onBlur={handleBlur}
                               value={values.accessCode}
                               required={true}/>
                        {errors.sessionTitle && touched.sessionTitle && errors.sessionTitle}
                    </div>
                    <div className="mt-3 form-group">
                        <input type="text"
                               className="form-control form-control-user text-center"
                               name="startDate"
                               placeholder="Start Date, e.g. 12/12/2020 02:23 PM"
                               autoFocus={true}
                               onChange={handleChange}
                               onBlur={handleBlur}
                               value={values.accessCode}
                               required={true}/>
                        {errors.startDate && touched.startDate && errors.startDate}
                    </div>
                    <div className="mt-3 form-group">
                        <input type="text"
                               className="form-control form-control-user text-center"
                               name="meetingLink"
                               placeholder="Start Date, e.g. 12/12/2020 02:23 PM"
                               autoFocus={true}
                               onChange={handleChange}
                               onBlur={handleBlur}
                               value={values.accessCode}
                               required={true}/>
                        {errors.meetingLink && touched.meetingLink && errors.meetingLink}
                    </div>
                    <div className="card mb-0" onClick={handleToggle}>
                        <div
                            className="mycard-header card-header"
                        >
                            <span className="card-title">Advanced Options</span>
                        </div>
                        <Collapse in={toggle}>
                         <div id="collapseOne"
                         className="card-body ">
                            <h5>Invite email template text</h5>
                            The template has be written the python format string format. The following variables are
                            available:<br/>
                            <table className="table table-responsive">
                                <thead>
                                <tr>
                                    <th scope="col">Name</th>
                                    <th scope="col">Meaning</th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr>
                                    <th scope="row" className="monospace">name</th>
                                    <td>Voter's name if set</td>
                                </tr>
                                </tbody>
                            </table>

                            Here is an example:<br/>
                            <p className="monospace">Dear,<br/><br/>You have been invited to our awesome meeting title.
                                We are meeting
                                on &#123;meeting_link&#125;. It
                                takes place on the &#123;start_date_en&#125; at &#123;start_time_en&#125;. You can login with the following
                                link:
                                &lt;a href="&#123;login_url&#125;"&gt; &#123;login_url&#125; &lt;/a&gt;.
                                You can also use the following access code on &#123;base_url&#125;: &#123;access_code&#125;<br/><br/>
                                    Best regards,<br/>
                                    Your awesome Organizers
                            </p>

                            <p>
                                Invite Text
                            </p>
                            <br/><br/>
                                <h6>Send test mail</h6>
                                <div className="form-row">
                                    <div className="col-8">
                                        Email
                                    </div>
                                    <div className="col">
                                        <button type="submit" id="id_btn_send_test"
                                                className="btn btn-warning btn-block" name="submit_type"
                                                value="test">
                                            Send test mail
                                        </button>
                                    </div>
                                </div>
                        </div>
                        </Collapse>
                        </div>
                    <div className="d-grid mt-2">
                        <button type="submit" id="id_btn_start" className="btn btn-success">Create Session</button>
                    </div>
                </form>
                )}
        </Formik>
      </div>
    );

    return (
        <Layout title="addSession">
            <div className="row justify-content-center">
                <div className="col-12">
                    <div className="card shadow">
                        <div className="card-body">
                            <Basic/>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}