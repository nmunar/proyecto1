import React from "react";
import { Button } from "react-bootstrap";

const LogoutButton = (props) => {
  return (
    <Button variant="outline-success" onClick={props.funcLogout()}>
      Logout
    </Button>
  );
};

export default LogoutButton;
