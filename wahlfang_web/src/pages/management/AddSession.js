import React, {useState} from 'react';
import Layout from "../../components/Layout";
import { Formik, Form, Field } from 'formik';
import Collapse from 'react-bootstrap/Collapse';
import Button from 'react-bootstrap/Button';
import * as yup from 'yup';
import {createSession} from "../../api/management";
import {Redirect, useHistory} from "react-router-dom";
import moment from "moment";
import TextField from '@mui/material/TextField';
import BasicDatePicker from "../../components/BasicDatePicker"
import {useRecoilState} from "recoil";
import {sessionList} from "../../state/management";



export default function AddSession() {
    const [toggle, setToggle] = useState(false);
    const [date, onDateChange] = useState(new Date());
    const [sessions, setSessions] = useRecoilState(sessionList);
    const history = useHistory();


    const handleSubmitAddSessionForm = (values, {setSubmitting}) => {
        let moment_date = new moment(values.start_date);
        // keepOffset must be true, bug info here https://github.com/moment/moment/issues/947
        values.start_date = moment_date.toISOString(true)
        createSession(values)
            .then(res => {
                setSubmitting(false)
                window.location.assign('/management/sessions');
                // TODO: Find out why recoil state is not reloaded when pushing the history
                // history.push("/management/sessions")
            })
            .catch(err => {
                const err_beauty = JSON.stringify(err, null, 4);
                console.log(err_beauty)
                setSubmitting(false);
            })
    }
    const handleSubmitTestEmail = (values) => {
        console.log(values)
    }


    const handleToggle = () => {
        setToggle(!toggle)
    }

    const validate = values => {
        const errors = {}
        if (!values.testEmail && toggle) {
            errors.testEmail = "Email must be set for sending the test mail.";
        }
        return errors;
    }

    const validationSchema = yup.object({
      title: yup
        .string("Session's title")
        .required('Please provide a session title')
    });

    const validationSchemaTestEmail = yup.object({
        testEmail: yup
            .string("Test Email")
            .email("Not a valid email")
            .required('Email must be set for sending the test mail.'),
        textArea: yup
            .string("Email here")
            .required('Email text cannot be empty.')
    })

    const AddSessionForm = () => (
      <div className="p-5">
        <Formik
          initialValues={{ title: '', start_date: '', meeting_link: ''}}
          validationSchema={validationSchema}
          onSubmit={handleSubmitAddSessionForm}
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
                <form id="add-session-form" onSubmit={(e) => {
                    e.preventDefault();
                    handleSubmit();
                  }}>
                    <h4>Create Session</h4>
                    <div className="mt-3 form-group">
                        <TextField
                        style ={{width: '100%'}}
                        id="title"
                        variant="standard"
                        name="title"
                        label="Session's Title"
                        value={values.title}
                        onChange={handleChange}
                        error={errors.title && touched.title && errors.title}
                        helperText={touched.title && errors.title}
                        />
                    </div>
                    <div className="mt-3 form-group">
                        <Field component={BasicDatePicker} name="start_date" onChange={handleChange}/>
                    </div>
                    <div className="mt-3 form-group">
                        <TextField
                        style ={{width: '100%'}}
                        id="meetingLink"
                        variant="standard"
                        name="meetingLink"
                        label="Link to meeting call platform (optional)"
                        value={values.meetingLink}
                        onChange={handleChange}
                        error={errors.meetingLink && touched.meetingLink && errors.meetingLink}
                        helperText={touched.meetingLink && errors.meetingLink}
                        />
                    </div>
                </form>
                )}
        </Formik>
      </div>
    );
    // TODO: Change advanced options to accordion
    const SendTestEmailForm = () => (
         <div>
        <Formik
        initialValues={{ testEmail: '', textArea: ''}}
        validationSchema={validationSchemaTestEmail}
        onSubmit={handleSubmitTestEmail}
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
            <form id="testEmailForm" onSubmit={(e) => {
                    e.preventDefault();
                    handleSubmit();
                  }}>
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
                                <TextField
                                    style ={{width: '100%'}}
                                    id="textArea"
                                    label="Your mail here..."
                                    multiline
                                    rows={8}
                                    variant="standard"
                                    onChange={handleChange}
                                    values={values.textArea}
                                    error={errors.textArea && touched.textArea && errors.textArea}
                                    helperText={touched.textArea && errors.textArea}
                                />
                            </div>
                            <br/><br/>
                                <h6>Send test mail</h6>
                                <div className="form-row d-flex">
                                    <div className="col-8">
                                        <TextField
                                            style ={{width: '100%'}}
                                            id="testEmail"
                                            variant="standard"
                                            name="meetingLink"
                                            label="your@email.de"
                                            values={values.testEmail}
                                            onChange={handleChange}
                                            error={errors.testEmail && touched.testEmail && errors.testEmail}
                                            helperText={touched.testEmail && errors.testEmail}
                                            />
                                    </div>
                                    <div className="col-4 text-center">
                                            <button type="submit" id="id_btn_send_test"
                                            className="btn btn-warning btn-block">
                                        Send test mail
                                        </button>
                                    </div>
                                </div>
                        </div>
                        </Collapse>
                        </div>
            </form>
                )}
        </Formik>
         </div>
    )

    return (
        <Layout title="addSession">
            <div className="row justify-content-center">
                <div className="col-12">
                    <div className="card shadow">
                        <div className="card-body">
                            <AddSessionForm/>
                            <SendTestEmailForm/>
                            <div className="d-grid mt-3">
                                <button type="submit" id="id_btn_start" className="btn btn-success" form="add-session-form">Create Session</button>
                         </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}