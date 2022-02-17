import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Modal, Button, Form } from "react-bootstrap";

export default function Register(props) {
  const [show, setShow] = useState(false);

  const handleShow = () => setShow(true);
  const handleClose = () => setShow(false);

  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  function register(evt) {
    if (!email.includes("@")) {
      alert("Introduzca un correo válido");
      return;
    }
    if (password != confirmPassword) {
      alert("Las contraseñas no coinciden");
      return;
    }

    fetch("http://127.0.0.1:5000/api/register", {
      method: "POST",
      body: JSON.stringify({
        nombres: nombre,
        apellidos: apellido,
        email: email,
        contrasena: password,
      }),
    })
      .then((resp) => {
        if (resp["status"] === 400) {
          alert("El correo ya esta en uso");
        } else {
          return resp.json();
        }
      })
      .then((json) => {
        if (json === undefined) return;
      })
      .catch((err) => {
        alert("Fallo en el registro: " + err);
      });
  }

  return (
    <>
      <Button
        variant="outline-success"
        onClick={handleShow}
        id="registerButton"
      >
        Registrase
      </Button>
      <Modal show={show}>
        <Modal.Header>
          <Modal.Title>Registrarse</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group
              className="mb-3"
              controlId="formBasicNombre"
              onChange={(evt) => setNombre(evt.target.value)}
            >
              <Form.Label>Nombres</Form.Label>
              <Form.Control type="text" placeholder="Ingresa tus nombres" />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="formBasicApellido"
              onChange={(evt) => setApellido(evt.target.value)}
            >
              <Form.Label>Apellidos</Form.Label>
              <Form.Control type="text" placeholder="Ingresa tus apellidos" />
            </Form.Group>
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
            <Form.Group
              className="mb-3"
              controlId="formBasicConfirmPassword"
              onChange={(evt) => setConfirmPassword(evt.target.value)}
            >
              <Form.Label>Verificar contraseña</Form.Label>
              <Form.Control
                type="password"
                placeholder="Verifica tu contraseña"
              />
            </Form.Group>
            <Button
              variant="primary"
              onClick={() => {
                if (
                  nombre == "" ||
                  apellido == "" ||
                  email == "" ||
                  password == "" ||
                  confirmPassword == ""
                ) {
                  alert("Debe completar todos los campos.");
                } else {
                  register();
                  handleClose();
                }
              }}
            >
              Registrarse
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
