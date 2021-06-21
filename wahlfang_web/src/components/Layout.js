import React from 'react'

import Header from "./Header";

export default function Layout({title, children}) {
    return (
            <article className="container mt-4" role="main">
                <div className="row justify-content-center">
                    <div className="col-lg-7 col-md-12">
                        {children}
                    </div>
                </div>
            </article>
    )
}