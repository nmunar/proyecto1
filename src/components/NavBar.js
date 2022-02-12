import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Fade from 'react-bootstrap/Fade';

function Options(logged, setLogged){
    const [login, setLogin] = useState(false)
    const [register, setRegister] = useState(false)

    function logOut(){
        setLogged(false)
        localStorage.clear()
        window.location.replace('/')
    }

    if(!logged){
        return(
            <div></div>
        )
    }
    else{
        return(
            <Button onClick={() => logOut()}>Log Out</Button>
        )
    }

}

export default function NavigationBar(props){
    return(
        <React.Fragment>
            
        </React.Fragment>
    )

}