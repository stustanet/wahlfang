import React, {useState} from 'react';
import Layout from "../../components/Layout";
import { Formik, Form, Field } from 'formik';
import Collapse from 'react-bootstrap/Collapse';
import Button from 'react-bootstrap/Button';
import FormikDateTime from "../../components/FormikDateTime"


export default function AddSession() {
    const [toggle, setToggle] = useState(false);
    const [date, onDateChange] = useState(new Date());


    const handleSubmit = (values, {setSubmitting}) => {
        console.log("Adding session submit")
    }


    const handleToggle = () => {
        setToggle(!toggle)
    }

    const AddSessionForm = () => (
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
                    <h4>Create Session</h4>
                    <div className="mt-3 form-group">
                        <label>Session's Title*</label>
                        <input type="text"
                               className="form-control form-control-user"
                               name="sessionTitle"
                               autoFocus={true}
                               onChange={handleChange}
                               onBlur={handleBlur}
                               value={values.accessCode}
                               required={true}/>
                        {errors.sessionTitle && touched.sessionTitle && errors.sessionTitle}
                    </div>
                    <div className="mt-3 form-group">
                        <label>Meeting start (optional)</label>
                        <Field name="date" timeFormat={false} component={FormikDateTime} />
                    </div>
                    <div className="mt-3 form-group">
                        <label>Link to meeting call platform (optional)</label>
                        <input type="text"
                               className="form-control form-control-user"
                               name="meetingLink"
                               placeholder="http://bbb.com"
                               autoFocus={true}
                               onChange={handleChange}
                               onBlur={handleBlur}
                               value={values.accessCode}/>
                        {errors.meetingLink && touched.meetingLink && errors.meetingLink}
                    </div>

                    <div className="card border-0">
                        <Button
                    onClick={handleToggle}
                    aria-controls="collapseOne"
                    aria-expanded={toggle}
                    variant="secondary"
                    className="mt-3"
                    >
                        <span className="card-title">Advanced Options</span>
                    </Button>
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
                                    <th scope="row" className="monospace">&#123;name&#125;</th>
                                    <td>Voter's name if set</td>
                                </tr>
                                <tr>
                                    <th scope="row" className="monospace">&#123;title&#125;</th>
                                    <td>Session's title</td>
                                </tr>
                                <tr>
                                    <th scope="row" className="monospace">&#123;access_code&#125;</th>
                                    <td>Access code/token for the voter to login</td>
                                </tr>
                                <tr>
                                    <th scope="row" className="monospace">&#123;login_url&#125;</th>
                                    <td>URL which instantly logs user in</td>
                                </tr>
                                <tr>
                                   <th scope="row" className="monospace">&#123;base_url&#125;</th>
                                    <td>Will render to: https://vote.stustanet.de</td>
                                </tr>
                                <tr>
                                    <th scope="row" className="monospace">&#123;start_time&#125;</th>
                                    <td>Start time if datetime is set</td>
                                </tr>
                                <tr>
                                    <th scope="row" className="monospace">&#123;start_date&#125;</th>
                                    <td>Start date if datetime is set</td>
                                </tr>
                                <tr>
                                    <th scope="row" className="monospace">&#123;start_time_en&#125;</th>
                                    <td>Start time in english format e.g. 02:23 PM</td>
                                </tr>
                                <tr>
                                   <th scope="row" className="monospace">&#123;start_date_en&#125;</th>
                                    <td>Start date in english format e.g. 12/12/2020</td>
                                </tr>
                                <tr>
                                    <th scope="row" className="monospace">&#123;meeting_link&#125;</th>
                                    <td>Meeting link if set</td>
                                </tr>
                                </tbody>
                            </table>

                            Here is an example: <br/><br/>
                            <p style={{ fontFamily: 'monospace' }}>Dear,<br/><br/>You have been invited to our awesome meeting title.
                                We are meeting
                                on &#123;meeting_link&#125;. It
                                takes place on the &#123;start_date_en&#125; at &#123;start_time_en&#125;. You can login with the following
                                link:
                                &lt;a href="&#123;login_url&#125;"&gt; &#123;login_url&#125; &lt;/a&gt;.
                                You can also use the following access code on &#123;base_url&#125;: &#123;access_code&#125;<br/><br/>
                                    Best regards,<br/>
                                    Your awesome Organizers
                            </p>

                            <div className="form-group mt-3">
                                <textarea  placeholder="Your mail here..." className="form-control" id="exampleFormControlTextarea1" rows="8"></textarea>
                            </div>
                            <br/><br/>
                                <h6>Send test mail</h6>
                                <div className="form-row d-flex">
                                    <div className="col-8">
                                             <input type="text"
                                           className="form-control form-control-user text-center"
                                           name="testEmail"
                                           placeholder="your@email.de"
                                           autoFocus={true}
                                           onChange={handleChange}
                                           onBlur={handleBlur}
                                           value={values.accessCode}
                                           required={true}/>
                                    </div>
                                    <div className="col-4 text-center">
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
                    <div className="d-grid mt-3">
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
                            <AddSessionForm/>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}