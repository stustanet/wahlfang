import React, {useEffect} from 'react';
import Layout from "../../components/Layout";
import {useParams} from "react-router-dom";
import {useRecoilValue} from "recoil";
import {sessionById} from "../../state/management"
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import MenuIcon from '@mui/icons-material/Menu';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import Box from "@mui/material/Box";
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';




export default function SessionDetail() {
    const {id} = useParams();
    const session = useRecoilValue(sessionById(parseInt(id)))
    console.log(session)


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
            <Box
            sx = {{
                 boxShadow: 1,
                 display: 'flex',
                 justifyContent: 'space-between',
                 p: 2,
                bgcolor: 'common.black'
            }}
            >
            <Typography variant="h4" color="common.white" component="div">
                {session.title}
            </Typography>
                <Box>
                    <Button
                            id="add-election-btn"
                            variant="contained"
                          >
                        Add Election
                          </Button>
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
                </Box>
            </Box>
            <Box
                sx = {{
                    boxShadow: 1,
                    display: 'flex',
                    p: 2,
                    justifyContent: 'left',
                }}
            >
                <Card
                sx = {{
                    border: "none"
                }}
                >
                    <CardContent>
                        There are no elections
                    </CardContent>
                </Card>
            </Box>
        </Layout>

    )
}