import React, { useState } from "react";
import { Button } from "react-bootstrap";

const LoginButton = (props) => {
  const [isAuthenticated, setAuthentication] = useState(false);

  const loginWithRedirect = () => {
    setAuthentication(true);
    props.funcAuth(true);
  };

  const logoutWithRedirect = () => {
    setAuthentication(false);
    props.funcAuth(false);
  };

  return (
    <div>
      {!isAuthenticated ? (
        <Button variant="outline-success" onClick={() => loginWithRedirect()}>
          Login
        </Button>
      ) : (
        <Button variant="outline-success" onClick={() => logoutWithRedirect()}>
          Logout
        </Button>
      )}
    </div>
  );
};

export default LoginButton;
