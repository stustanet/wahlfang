import React from 'react'

import Header from "./Header";

export default function Layout({title, children}) {
    return (
        <div id="content">
            <Header/>
            <article className="container mt-4" role="main">
                {children}
            </article>
        </div>
    )
}