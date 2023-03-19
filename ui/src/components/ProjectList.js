import React, { useState, useEffect } from "react";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { Button } from "@mui/material";
import Box from '@mui/material/Box';
import NativeSelect from '@mui/material/NativeSelect';
import Modal from '@mui/material/Modal';
import { Link } from "react-router-dom";

export const ProjectList = (props) => {

    //stores projects in an array. Each project contains project_id, created_on, article_title, target_language, assigned_to, created_by
    const [projects, setProjects] = useState([]);
    //stores title. Used while creating new project
    const [title, setTitle] = useState("");
    //stores language. Used while creating new project. Default language is set to Tamil
    const [language, setLanguage] = useState("ta");
    //stores user_id, which refers to the assignee for the project
    const [assignee, setAssignee] = useState(-1);
    //stores the list of all users
    const [users, setUsers] = useState({});
    //stores the current user id
    const [currUser, setCurrUser] = useState(null);
    //state used to control the Modal opening and closing
    const [open, setOpen] = useState(false);
    //Stores error message
    const [errorMessage, setErrorMessage] = useState("");

    //Style for Modal's Box
    const style = {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 400,
        bgcolor: 'background.paper',
        border: '2px solid #000',
        boxShadow: 24,
        p: 4,
        backgroundImage: 'linear-gradient(79deg, #7439db, #C66FBC 48%, #F7944D)',
    };

    //handle function for opening Modal
    const handleOpen = () => {
        setOpen(true);
        setTitle("");
    }
    //handle function for closing Modal
    const handleClose = () => setOpen(false);

    //Runs whenever Modal is opened/closed. Also run when the page is rendering for the first time
    useEffect(() => {
        //AJAX call to get the user list
        fetch("http://localhost:8000/wiki/users/", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("wiki-trans-token")}`
            }
        }).then(response => {
            if (response.status == 401) {
                //If the user is not authenticated, it routes to login page.
                window.location.href = '/login';
            }
            return response.json()
        })
        .then(data => {
            if (data['error']) {
                //Incase we get a error response, we throw it here and store in errorMessage state
                throw Error(data['error']);
            }
            //Otherwise set the values
            setUsers(data['users'])
            setCurrUser(data['current_user'])
        }).catch((error) => setErrorMessage(error.message))

        //AJAX call for getting the project list
        fetch("http://localhost:8000/wiki/", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("wiki-trans-token")}`
            }
        }).then(response => {
            if (response.status == 401) {
                //If the user is not authenticated, it routes to login page.
                window.location.href = '/login';
            }
            return response.json()
        })
        .then(data => {
            if (data['error']) {
                //Incase we get a error response, we throw it here and store in errorMessage state
                throw Error(data['error']);
            }
            setProjects(data);
        }).catch((error) => setErrorMessage(error.message))
    }, [open]);

    //Function for handling creation of new project
    const handleSubmit = (event) => {
        event.preventDefault();

        //AJAX call for saving a new project
        fetch('http://localhost:8000/wiki/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("wiki-trans-token")}`
            },
            body: JSON.stringify({
                article_title: title,
                target_language: language,
                assigned_to: assignee
            })
        }).then(response => {
            if (response.status == 401) {
                //If the user is not authenticated, it routes to login page.
                window.location.href = '/login';
            }
            return response.json();
        })
        .then(data => {
            if (data['error']) {
                //Incase we get a error response, we throw it here and store in errorMessage state
                throw Error(data['error']);
            }
            setOpen(false);
        }).catch((error) => setErrorMessage(error.message))
    }
    
    //Function to handle assignee change at dashboard
    const handleAssigneeChange = (event, project_id) => {
        //AJAX call to update the assignee
        fetch('http://localhost:8000/wiki/project/' + project_id, {
            method: 'PATCH',
            body: JSON.stringify({
                assigned_to: event.target.value,
            }),
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("wiki-trans-token")}`
            }
        }).then(response => {
            if (response.status == 401) {
                //If the user is not authenticated, it routes to login page.
                window.location.href = '/login';
            }
            return response.json();
        })
        .then(data => {
            if (data['error']) {
                //Incase we get a error response, we throw it here and store in errorMessage state
                throw Error(data['error']);
            }
            console.log("assignee changed..");
        }).catch((error) => setErrorMessage(error.message))
        //Changing state to show the new assignee
        setAssignee(event.target.value);
    }

    //Time out set to 5 sec for showing error messages
    setTimeout(() => {
        setErrorMessage("");
    }, 5000);


    //Function to handle signout
    const handleSignOut = (event) => {
        //Clear all the localStorage and redirect to login page
        localStorage.clear()
        window.location.href = '/login';
    }

    return (<div>
        {/* Header */}
        <header className="header">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginLeft: '20px', marginRight: '20px' }}>
                <h3>Wikipedia Translator</h3>
                <Button variant="contained" onClick={handleSignOut}>
                    Sign Out
                </Button>
            </div>
        </header>

        {/* Shows error message if the model is not open */}
        {!open && <p>{errorMessage}</p>}

        {/* If there are project, it is shown in table with 3 columns: Project ID, Created By, Assigned To
        else No project available is shown */}

        {projects.length == 0 ? <p>No projects available</p> : 
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <TableHead>
                        <TableRow>
                            {/* Table Topics */}
                            <TableCell>Project ID</TableCell>
                            <TableCell align="right">Created By</TableCell>
                            <TableCell align="right">Assigned To</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {projects.map((project) => ( 
                            <TableRow
                                key={project['project_id']}
                                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                            >
                                {/* Values for each project */}
                                <TableCell component="th" scope="row">
                                    <Link to={"/project/" + project['project_id']}>{project['project_id']}</Link>
                                </TableCell>
                                <TableCell align="right"> {users[project['created_by']]['name']} </TableCell>
                                <TableCell align="right">
                                    <NativeSelect
                                        disabled={(users[currUser] && users[currUser]['canAdd'] == 1) ? false : true}
                                        defaultValue={project['assigned_to']}
                                        onChange={(event) => {handleAssigneeChange(event, project['project_id'])}}
                                    >
                                        <option value={-1} key={-1}>Choose an assignee</option>
                                        {Object.keys(users).map((id) => (
                                            <option value={id} key={id}>{users[id]['name']}</option>
                                        ))}
                                    </NativeSelect>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        }
        {/* Button for creating new project */}
        <Button variant="outlined" onClick={handleOpen} disabled={(users[currUser] && users[currUser]['canAdd'] == 1) ? false : true}>Add New Project</Button>
        {/* Modal used for creating new project */}
        <Modal
            open={open}
            onClose={handleClose}
            aria-labelledby="modal-modal-title"
            aria-describedby="modal-modal-description"
        >
            <Box sx={style}>
                {/* error message is displayed on the Modal box */}
                {errorMessage.length != 0 && <div className="error-message">{errorMessage}</div>}
                <h2>Create New Project</h2>
                <form className="create-new-project" onSubmit={handleSubmit}>
                    <label htmlFor="title">Title</label>
                    <input value={title} onChange={(e) => setTitle(e.target.value)} type="text" placeholder="title" id="title" name="title" />
                    <label htmlFor="language">Language</label>
                    <NativeSelect
                        defaultValue={language}
                        onChange={(event) => {setLanguage(event.target.value)}}
                    >
                        <option value='bn'>Bengali</option>
                        <option value='gu'>Gujarati</option>
                        <option value='hi'>Hindi</option>
                        <option value='kn'>Kannada</option>
                        <option value='ml'>Malayalam</option>
                        <option value='mr'>Marathi</option>
                        <option value='ne'>Nepali</option>
                        <option value='or'>Oriya</option>
                        <option value='pa'>Panjabi</option>
                        <option value='si'>Sinhala</option>
                        <option value='ta'>Tamil</option>
                        <option value='te'>Telugu</option>
                        <option value='ur'>Urdu</option>
                    </NativeSelect>

                    <label htmlFor="assignee">Assignee</label>
                    <NativeSelect
                        defaultValue={assignee}
                        onChange={(event) => {setAssignee(event.target.value)}}
                    >
                        <option value={-1} key={-1}>Choose an assignee</option>
                        {Object.keys(users).map((id) => (
                            <option value={id} key={id}>{users[id]['name']}</option>
                        ))}
                    </NativeSelect>
                    <button type="submit">Create</button>
                </form>
            </Box>
        </Modal>
    </div>);
}