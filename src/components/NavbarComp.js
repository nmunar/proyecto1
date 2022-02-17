import React, { useState } from "react";
import { Navbar, Container, Button } from "react-bootstrap";
import Login from "./Login";
import Register from "./Register";
import "./Navbar.css";

function Options(logged, setLogged) {
  function logOut() {
    setLogged(false);
    localStorage.clear();
    window.location.replace("/");
  }

  if (!logged) {
    return (
      <>
        <div id="buttonContainer">
          <Login logged={logged} setLogged={setLogged} id="loginButton" />
          <Register />
        </div>
      </>
    );
  } else {
    return (
      <Button variant="outline-success" onClick={() => logOut()}>
        Cerrar sesión
      </Button>
    );
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
