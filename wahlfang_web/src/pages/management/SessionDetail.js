import React, {useEffect} from 'react';
import Layout from "../../components/Layout";
import {useRecoilValue} from "recoil";
import {sessionList} from "../../state/management"
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import MenuIcon from '@mui/icons-material/Menu';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';

export default function ManagerSessions() {
    const data = useRecoilValue(sessionList)

    const [anchorEl, setAnchorEl] = React.useState(null);
    const open = Boolean(anchorEl);
    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };
    return (
        <Layout>
            {data.map(session => (
                <div className="row justify-content-center">
                    <div className="col-12">
                        <div className="card shadow">
                            <div className="card-header bg-dark text-light">
                                <h4 className="d-inline">{session.title}</h4>
                                <div className="d-inline float-right">
                                    <Button
                                        id="demo-positioned-button"
                                        aria-controls="demo-positioned-menu"
                                        aria-haspopup="true"
                                        aria-expanded={open ? 'true' : undefined}
                                        onClick={handleClick}
                                        startIcon={<MenuIcon />}
                                      >
                                      </Button>
                                      <Menu
                                        id="demo-positioned-menu"
                                        aria-labelledby="demo-positioned-button"
                                        anchorEl={anchorEl}
                                        open={open}
                                        onClose={handleClose}
                                        anchorOrigin={{
                                          vertical: 'top',
                                          horizontal: 'left',
                                        }}
                                        transformOrigin={{
                                          vertical: 'top',
                                          horizontal: 'left',
                                        }}
                                      >
                                        <MenuItem onClick={handleClose}>Profile</MenuItem>
                                        <MenuItem onClick={handleClose}>My account</MenuItem>
                                        <MenuItem onClick={handleClose}>Logout</MenuItem>
                                      </Menu>
                                </div>
                                </div>
                            </div>
                        </div>
                    </div>
            ))}
        </Layout>
    )
}