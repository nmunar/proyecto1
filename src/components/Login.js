import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Modal, Button, Form } from "react-bootstrap";

export default function Login(props) {
  const [show, setShow] = useState(false);

  const handleShow = () => setShow(true);
  const handleClose = () => setShow(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function login(evt) {
    if (!email.includes("@")) {
      alert("Introduce a valid email");
      return;
    }

    fetch("http://127.0.0.1:5000/api/login", {
      method: "POST",
      body: JSON.stringify({
        email: email,
        contrasena: password,
      }),
    })
      .then((resp) => resp.json())
      .then((json) => {
        if (json["status_code"] == 401) {
          alert("The email or the password doesn't match");
          return;
        }
        localStorage.setItem("email", email);
        localStorage.setItem("access_token", json["access_token"]);
        props.setLogged(true);
        window.location.reload();
      })
      .cath((err) => {
        alert("Failed login:" + err);
      });
  }

  return (
    <>
      <Button variant="outline-success" onClick={handleShow} id="loginButton">
        Iniciar sesión
      </Button>
      <Modal show={show}>
        <Modal.Header>
          <Modal.Title>Iniciar sesión</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group
              className="mb-3"
              controlId="formBasicEmail"
              onChange={(evt) => setEmail(evt.target.value)}
            >
              <Form.Label>Correo</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ingresa tu correo electrónico"
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="formBasicPassword"
              onChange={(evt) => setPassword(evt.target.value)}
            >
              <Form.Label>Contraseña</Form.Label>
              <Form.Control
                type="password"
                placeholder="Ingresa tu contraseña"
              />
            </Form.Group>
            <Button
              variant="primary"
              onClick={() => {
                if (email == "" || password == "") {
                  alert("Debe completar todos los campos.");
                } else {
                  login();
                  handleClose();
                }
              }}
            >
              Iniciar sesión
            </Button>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={handleClose} varian="secondary">
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
