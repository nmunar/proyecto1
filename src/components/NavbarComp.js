import React, { useState } from "react";
import { Navbar, Container } from "react-bootstrap";
import LoginButton from "./LoginButton";

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
