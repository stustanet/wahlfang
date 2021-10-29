import React, {Fragment, useEffect} from 'react';
import Layout from "../../components/Layout";
import {useRecoilState} from "recoil";
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
import {deleteSession} from "../../api/management"
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';



export default function ManagerSessions() {
    const [open, setOpen] = React.useState(false);
    const [index, setIndex] = React.useState(0);
    const [sessions, setSessions] = useRecoilState(sessionList);
    const history = useHistory();

      const handleClickOpen = (e, index) => {
        e.stopPropagation();
        setOpen(true);
        setIndex(index);
      };

      const handleClose = () => {
        setOpen(false);
      };

    const formatDate = (start_date) => {
        return moment(start_date).format("LLLL")
    }

    const toCreateSession = () => {
        const path = "/management/add-session";
        history.push(path);
    }

    const handleDelete = (pk) => {
        deleteSession(pk)
            .then(res => {
                const sessions_left = sessions.filter(session => session.id !== pk)
                setSessions(sessions_left)
            })
            .catch(err => {
                console.log(err)
            })
        handleClose();
    }

    const toSessionDetail = (pk) => {
        console.log("Stopping in detail view")
        history.push(`/management/sessions/${pk}`)
    }

    return (

          <Layout>
              <div className="row justify-content-center">
                <div className="col-12">
                    <div className="card shadow">
                        <div className="card-body">
                             <h4>My Sessions</h4>
                            {sessions.map((session, index) => (
                                <Box key={session.id} pb={3} sx={{ width: '100%', bgcolor: 'background.paper', }}>
                                      <List component="nav" aria-label="main mailbox folders">
                                        <ListItemButton onClick={() => toSessionDetail(session.id)}>
                                         <ListItemText disableTypography
                                            primary={<Typography type="body2" style={{ color: '#495057' }}>{session.title}</Typography>} />
                                            {session.start_date && <ListItemText sx={{pr: 2}} primary={<Typography align="right" type="overline" style={{ color: '#495057' }}>{formatDate(session.start_date)}</Typography>}/>}
                                            <Button onClick={(e) => handleClickOpen(e, index)}
                                                variant="outlined" startIcon={<DeleteIcon />} color="error"> Delete </Button>
                                        </ListItemButton>
                                      </List>
                                      <Divider />
                                    </Box>
                            ))}
                            <Dialog
                            open={open}
                            onClose={handleClose}
                            aria-labelledby="alert-dialog-title"
                            aria-describedby="alert-dialog-description"
                          >
                            <DialogTitle id="alert-dialog-title">
                              {"Are you sure you want to delete this session?"}
                            </DialogTitle>
                            <DialogActions>
                              <Button onClick={handleClose}>Cancel</Button>
                              <Button color="error" onClick={() => handleDelete(sessions[index].id)} autoFocus>
                                Delete
                              </Button>
                            </DialogActions>
                          </Dialog>
                        <Button onClick={toCreateSession} variant="contained" color="success">Create Session</Button>
                     </div>
                </div>
            </div>
        </div>
        </Layout>
    )
}