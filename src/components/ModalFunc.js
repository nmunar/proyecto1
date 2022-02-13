import React from "react";
import { useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";

const ModalFunc = (props) => {
  const [show, setShow] = useState(false);

  const handleShow = () => setShow(true);
  const handleClose = () => setShow(false);

  const [nombre, setNombre] = useState("");
  const [imagen, setImagen] = useState("");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [valorPagar, setValorPagar] = useState(0);
  const [guion, setGuion] = useState("");
  const [recomendaciones, setRecomendaciones] = useState("");

  return (
    <>
      <Button variant="outline-success" onClick={handleShow}>
        Crear un nuevo concurso
      </Button>
      <Modal show={show}>
        <Modal.Header>
          <Modal.Title>Crear concurso</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group
              className="mb-3"
              controlId="formBasicNombre"
              onChange={(evt) => setNombre(evt.target.value)}
            >
              <Form.Label>Nombre</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ingrese el nombre del concurso"
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="formBasicImagen"
              onChange={(evt) => setImagen(evt.target.value)}
            >
              <Form.Label>Imagen</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ingrese la URL de la imagen del concurso"
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="formBasicFI"
              onChange={(evt) => setFechaInicio(evt.target.value)}
            >
              <Form.Label>Fecha de inicio</Form.Label>
              <Form.Control
                type="datetime-local"
                placeholder="Ingrese la fecha de inicio del concurso"
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="formBasicFF"
              onChange={(evt) => setFechaFin(evt.target.value)}
            >
              <Form.Label>Fecha de finalización</Form.Label>
              <Form.Control
                type="datetime-local"
                placeholder="Ingrese la fecha de finalización del concurso"
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="formBasicValorPagar"
              onChange={(evt) => setValorPagar(evt.target.value)}
            >
              <Form.Label>Valor a pagar</Form.Label>
              <Form.Control
                type="number"
                placeholder="Ingrese el valor a pagar"
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="exampleForm.ControlTextarea1"
              onChange={(evt) => setGuion(evt.target.value)}
            >
              <Form.Label>Guión</Form.Label>
              <Form.Control as="textarea" rows={3} />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="exampleForm.ControlTextarea1"
              onChange={(evt) => setRecomendaciones(evt.target.value)}
            >
              <Form.Label>Recomendaciones</Form.Label>
              <Form.Control as="textarea" rows={3} />
            </Form.Group>
            <Button
              variant="primary"
              onClick={() => {
                if (
                  nombre == "" ||
                  imagen == "" ||
                  fechaInicio == "" ||
                  fechaFin == "" ||
                  valorPagar == 0 ||
                  guion == "" ||
                  recomendaciones == ""
                ) {
                  alert("Debe completar todos los campos.");
                } else {
                  props.funcCreate(
                    nombre,
                    imagen,
                    fechaInicio,
                    fechaFin,
                    valorPagar,
                    guion,
                    recomendaciones
                  );
                  handleClose();                  
                  window.location.reload()
                }
              }}
            >
              Crear evento
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
};

export default ModalFunc;
