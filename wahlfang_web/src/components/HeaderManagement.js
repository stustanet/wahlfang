import {Link} from "react-router-dom";
import {useRecoilValue} from "recoil";
import {isManagerAuthenticated} from "../state/management";
import logo from '../assets/logo_inv.png';


export default function HeaderManagement() {
    const authenticated = useRecoilValue(isManagerAuthenticated);

    return (
    <nav className="navbar navbar-expand navbar-dark bg-dark shadow">
        <div className="container">
            <Link className="navbar-brand" to="/management/sessions">
                <img src={logo} alt="StuStaNet" width="192px"/>
            </Link>
            <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarNav">
                <div className="navbar-text me-auto">Online Voting System</div>
                <ul className="navbar-nav">
                    <li className="nav-item">
                        <Link className="nav-link" to="/management/help">Help</Link>
                    </li>
                    {authenticated ? (
                        <Link className="nav-link" to="/management/logout">Logout</Link>
                    ): ""}
                </ul>
            </div>
        </div>
    </nav>
    )
}