import React from 'react'

import Header from "./Header";

export default function Layout({title, children}) {
    return (
        <div id="content">
            <Header/>
            <article className="container mt-4" role="main">
                <div className="row justify-content-center">
                    <div className="col-lg-6 col-md-9 col-sm-12">
                        {children}
                    </div>
                </div>
            </article>
        </div>
    )
}