import React, { useState } from "react";
import { Navbar, Container } from "react-bootstrap";
import Login from "./Login";
import LoginButton from "./LoginButton";
import Register from "./Register";

function Options(logged, setLogged,funcAuth){
  const [login, setLogin] = useState(false)
  const [register, setRegister] = useState(false)

  function logOut(){
      setLogged(false)
      localStorage.clear()
      window.location.replace('/')
  }

  if(!logged){
      return(
        <>
        <LoginButton funcAuth={funcAuth} />
        <Login setLogged = {setLogged} />
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
