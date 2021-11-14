import React, {useState} from 'react';
import Layout from "../../components/Layout";
import { Formik, Form, Field } from 'formik';
import Collapse from 'react-bootstrap/Collapse';
import Button from 'react-bootstrap/Button';
import * as yup from 'yup';
import {createElection} from "../../api/management";
import {Redirect, useHistory, useParams} from "react-router-dom";
import moment from "moment";
import TextField from '@mui/material/TextField';
import BasicDatePicker from "../../components/BasicDatePicker"
import {useRecoilState} from "recoil";
import {electionsListManager} from "../../state/management";
import {DateTime} from 'luxon';



export default function CreateSession() {
    const [toggle, setToggle] = useState(false);
    const [date, onDateChange] = useState(new Date());
    const [elections, setElections] = useRecoilState(electionsListManager);
    // get session id from url
    const {id} = useParams();


    const handleSubmitAddElectionForm = (values, {setSubmitting}) => {
        let moment_date = new moment(values.start_date);
        // keepOffset must be true, bug info here https://github.com/moment/moment/issues/947
        values.start_date = moment_date.toISOString(true)
        values.end_date = moment_date.toISOString(true)
        values.session = id
        createElection(values)
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

    const validationSchema = yup.object({
      title: yup
        .string("Election name")
        .required('Please provide an election name'),
      start_date: yup.string().test("is-after-now", "start time should not be in the past", function(value){
          const now = new DateTime.now()
          return value > now
      }),
      end_date: yup
        .string()
        .test("is-greater", "end time should be greater", function(value) {
            console.log(this.parent.start_date)
            console.log(value)
            return value > this.parent.start_date
    })
    });

    const CreateElectionForm = () => (
      <div className="p-5">
        <Formik
          initialValues={{ title: '', start_date: '', end_date: '', maximum_votes: 0}}
          validationSchema={validationSchema}
          onSubmit={handleSubmitAddElectionForm}
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
                <form id="add-election-form" onSubmit={(e) => {
                    e.preventDefault();
                    handleSubmit();
                  }}>
                    <h4>Create Election</h4>
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
                        <Field component={BasicDatePicker} name="end_date" onChange={handleChange}/>
                    </div>
                    <div className="mt-3 form-group">
                        <TextField
                        style ={{width: '100%'}}
                        id="maximum_votes"
                        type="number"
                        label="Maximum number of votes"
                        variant="standard"
                        name="maximum_votes"
                        inputProps={{ min: 0 }}
                        value={values.maximum_votes}
                        onChange={handleChange}
                        error={errors.maximum_votes && touched.maximum_votes && errors.maximum_votes}
                        helperText={touched.maximum_votes && errors.maximum_votes}
                        />
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
                            <CreateElectionForm/>
                            <div className="d-grid mt-3">
                                <button type="submit" id="id_btn_start" className="btn btn-success" form="add-election-form">Create Election</button>
                         </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )

}