import React, { useState } from "react";
import ModalFunc from "./ModalFunc";
import { Table, Container, Button, Modal, Form } from "react-bootstrap";

const TableComp = (props) => {
  const [show, setShow] = useState(false);

  const handleShow = () => setShow(true);
  const handleClose = () => setShow(false);

  const [id, setId] = useState(0);
  const [nombre, setNombre] = useState("");
  const [imagen, setImagen] = useState("");
  const [fechaCreacion, setFechaCreacion] = useState("");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [valorPagar, setValorPagar] = useState(0);
  const [guion, setGuion] = useState("");
  const [recomendaciones, setRecomendaciones] = useState("");

  return (
    <Container fluid>
      <ModalFunc funcCreate={props.funcCreate} />
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>NOMBRE</th>
            <th>FECHA CREACIÓN</th>
            <th>FECHA INICIO</th>
            <th>FECHA FIN</th>
            <th>VALOR A PAGAR</th>
            <th>EDITAR</th>
            <th>ELIMINAR</th>
          </tr>
        </thead>
        <tbody>
          {Object.values(props.list).map((obj, index) => (
            <tr key={index}>
              <td>{obj.nombre}</td>
              <td>{obj.fechaCreacion}</td>
              <td>{obj.fechaInicio}</td>
              <td>{obj.fechaFin}</td>
              <td>{obj.valorPagar}</td>
              <td>
                <Button
                  variant="primary"
                  onClick={() => {
                    handleShow();
                    setId(obj.id);
                    setNombre(obj.nombre);
                    setImagen(obj.imagen);
                    setFechaCreacion(obj.fechaCreacion);
                    setFechaInicio(obj.fechaInicio);
                    setFechaFin(obj.fechaFin);
                    setValorPagar(obj.valorPagar);
                    setGuion(obj.guion);
                    setRecomendaciones(obj.recomendaciones);
                  }}
                >
                  Editar
                </Button>
              </td>
              <td>
                <Button
                  variant="danger"
                  onClick={() => {
                    props.funcDelete(obj.id);
                  }}
                >
                  Eliminar
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <Modal show={show}>
        <Modal.Header>
          <Modal.Title>Actualizar concurso</Modal.Title>
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
                defaultValue={nombre}
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
                defaultValue={imagen}
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
                defaultValue={fechaInicio}
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
                defaultValue={fechaFin}
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
                defaultValue={valorPagar}
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="exampleForm.ControlTextarea1"
              onChange={(evt) => setGuion(evt.target.value)}
            >
              <Form.Label>Guión</Form.Label>
              <Form.Control defaultValue={guion} as="textarea" rows={3} />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="exampleForm.ControlTextarea1"
              onChange={(evt) => setRecomendaciones(evt.target.value)}
            >
              <Form.Label>Recomendaciones</Form.Label>
              <Form.Control
                defaultValue={recomendaciones}
                as="textarea"
                rows={3}
              />
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
                  props.funcUpdate(
                    id,
                    nombre,
                    imagen,
                    fechaCreacion,
                    fechaInicio,
                    fechaFin,
                    valorPagar,
                    guion,
                    recomendaciones
                  );
                  handleClose();
                  window.location.reload();
                }
              }}
            >
              Actualizar concurso
            </Button>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={handleClose} varian="secondary">
            Cerrar
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default TableComp;
