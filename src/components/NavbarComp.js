import React, { useState } from "react";
import { Navbar, Container } from "react-bootstrap";
import LoginButton from "./LoginButton";

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

const NavbarComp = (props) => {
  return (
    <Navbar variant="dark" bg="dark" expand="lg">
      <Container>
        <Navbar.Brand>Concursos</Navbar.Brand>
        <LoginButton funcAuth={props.funcAuth} />
      </Container>
    </Navbar>
  );
};

export default NavbarComp;
