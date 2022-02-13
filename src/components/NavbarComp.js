import React, { useState } from "react";
import { Navbar, Container, Button } from "react-bootstrap";
import Login from "./Login";
import Register from "./Register";

function Options(logged, setLogged){

  function logOut(){
      setLogged(false)
      localStorage.clear()
      window.location.replace('/')
  }

  if(!logged){
      return(
        <>
        <Login logged = {logged} setLogged = {setLogged} />
        <Register />
        </>
      )
  }
  else{
      return(
          <Button onClick={() => logOut()}>Log Out</Button>
      )
  }

}

const NavbarComp = (props) => {
  return (
    <Navbar variant="dark" bg="dark" expand="lg">
      <Container>
        <Navbar.Brand>SuperVoices</Navbar.Brand>
        {Options(props.logged, props.setLogged, props.funcAuth)}
      </Container>
    </Navbar>
  );
};

export default NavbarComp;
