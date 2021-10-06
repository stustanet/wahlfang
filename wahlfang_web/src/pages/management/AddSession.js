import React from "react";
import {useHistory, useParams} from "react-router-dom";
import Layout from "../../components/Layout";
import {useFormik} from "formik";
import {useRecoilValue} from "recoil";
import {performVote} from "../../api";


export default function AddSession() {
    const history = useHistory();

    const formik = useFormik({
        onSubmit: values => {
    //        TO be defined is a function that calls the endpoint to create the session
    })
}