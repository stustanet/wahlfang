import React, {useEffect} from 'react';
import Layout from "../../components/Layout";
import {useParams} from "react-router-dom";
import {useRecoilValue, useSetRecoilState} from "recoil";
import {sessionById, electionsManagerBySessionId, electionsListManager} from "../../state/management"
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import MenuIcon from '@mui/icons-material/Menu';
import Box from "@mui/material/Box";
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import { CardHeader, Divider, IconButton } from '@mui/material';
import Typography from '@mui/material/Typography';
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import DeleteIcon from "@mui/icons-material/Delete";
import moment from "moment";
import DialogTitle from "@mui/material/DialogTitle";
import DialogActions from "@mui/material/DialogActions";
import Dialog from "@mui/material/Dialog";
import { red } from '@mui/material/colors';
import {deleteElection} from "../../api/management";



export default function SessionDetail() {
    const [openDialog, setOpenDialog] = React.useState(false);
    const [selectedElectionId, setSelectedElectionId] = React.useState(0);
    const [anchorEl, setAnchorEl] = React.useState(null);
    const open = Boolean(anchorEl);
    const {id} = useParams();
    const session = useRecoilValue(sessionById(parseInt(id)))
    const elections = useRecoilValue(electionsManagerBySessionId(parseInt(id)))
    const setElectionState = useSetRecoilState(electionsListManager)
    console.log(elections)


    const formatDate = (election) => {
        let displayDate = '';
        if (election.end_date && moment(election.end_date).isAfter()) {
            displayDate = "Closed"
        } else if (election.start_date && moment(election.start_date).isBefore()) {
            displayDate = `Open, needs to be closed manually`
        } else if (election.start_date && moment(election.start_date).isAfter()) {
            const start_date_moment = new moment(election.start_date)
            displayDate = `Starts on ${start_date_moment.format('LLLL')}`
        } else {
            displayDate = "Needs to be started manually"
        }
        return displayDate
    }
     const handleClickOpen = (e, index) => {
        e.stopPropagation();
        setOpenDialog(true);
        setSelectedElectionId(index);
      };

     const handleCloseDialog = () => {
        setOpenDialog(false);
      };
    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };


    const handleDeleteElection = (electionId) => {
        deleteElection(electionId)
            .then(res => {
                const elections_left = elections.filter(election => election.id !== electionId)
                setElectionState(elections_left)
            })
            .catch(err => {
                console.log(err)
            })
        handleCloseDialog();
    }

    const electionCard = (
        <React.Fragment>
            <CardHeader title="Open Elections"/>
            <Divider/>
            <CardContent>
                {
                elections.map((election, index) => (
                <Box key={election.id} pb={3} sx={{ width: '100%', bgcolor: 'background.paper', }}>
                      <List component="nav" aria-label="main mailbox folders">
                        <ListItemButton>
                         <ListItemText disableTypography
                            primary={<Typography style={{ color: '#495057' }}>{election.title}</Typography>} />
                            <ListItemText sx={{pr: 2}}
                                  primary={<Typography fontSize={14} align="right" type="overline" style={{ color: '#495057' }}>
                                      {formatDate(election)}</Typography>}/>
                              <IconButton variant="outlined" sx={{ color: red[500] }} onClick={(e) => handleClickOpen(e, index)}>
                                  <DeleteIcon/>
                              </IconButton>
                        </ListItemButton>
                      </List>
                      <Divider />
                    </Box>
                ))
                }
            </CardContent>
            <Dialog
            open={openDialog}
            onClose={handleCloseDialog}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
          >
            <DialogTitle id="alert-dialog-title">
              {"Are you sure you want to delete this session?"}
            </DialogTitle>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Cancel</Button>
              <Button onClick ={() => handleDeleteElection(elections[selectedElectionId].id)} color="error" autoFocus>
                Delete
              </Button>
            </DialogActions>
          </Dialog>
        </React.Fragment>
    )

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
                    border: "none",
                    width: "100%",
                    p: 1,
                }}
                >
                    {elections ?
                        electionCard
                        : <CardContent>
                        There are no elections
                    </CardContent>}

                </Card>
            </Box>
        </Layout>

    )
}