import React, {Fragment, useEffect} from 'react';
import Layout from "../../components/Layout";
import {useRecoilValue} from "recoil";
import {sessionList} from "../../state/management"
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import DeleteIcon from '@mui/icons-material/Delete';
import { Typography } from '@mui/material';
import { useHistory } from "react-router-dom";
import moment from "moment";



export default function ManagerSessions() {
    const data = useRecoilValue(sessionList);
    const history = useHistory();

    const formatDate = (start_date) => {
        return moment(start_date).format("LLLL")
    }

    const toCreateSession = () => {
        const path = "/management/add-session";
        history.push(path);
    }

    return (

          <Layout>
              <div className="row justify-content-center">
                <div className="col-12">
                    <div className="card shadow">
                        <div className="card-body">
                             <h4>My Sessions</h4>
                            {data.map(session => (
                                <Box pb={3} sx={{ width: '100%', bgcolor: 'background.paper', }}>
                                      <List component="nav" aria-label="main mailbox folders">
                                        <ListItemButton>
                                         <ListItemText disableTypography
                                            primary={<Typography type="body2" style={{ color: '#495057' }}>{session.title}</Typography>} />
                                            {session.start_date && <ListItemText sx={{pr: 2}} primary={<Typography align="right" type="overline" style={{ color: '#495057' }}>{formatDate(session.start_date)}</Typography>}/>}
                                            <Button variant="outlined" startIcon={<DeleteIcon />} color="error"> Delete </Button>
                                        </ListItemButton>
                                      </List>
                                      <Divider />
                                    </Box>
                            ))}
                        <Button onClick={toCreateSession} variant="contained" color="success">Create Session</Button>
                     </div>
                </div>
            </div>
        </div>
        </Layout>
    )
}