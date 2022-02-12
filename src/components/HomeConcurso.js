import React, { useState, useEffect } from 'react';
import { useParams } from "react-router-dom";
import { Button, Tabs, Tab, Form, Container, Navbar, Row, Col, Modal, Image } from "react-bootstrap";
import 'bootstrap/dist/css/bootstrap.css';

export default function HomeConcurso() {
    const [concurso, setConcurso] = useState({})
    const [idC, setId] = useState("")
    const [imagen, setImg] = useState("")
    const [nombreE, setNombreE] = useState("")
    const [apellidoE, setApellidoE] = useState("")
    const [emailE, setEmailE] = useState("")
    const [obs, setObsE] = useState("")
    const [key, setKey] = useState('home');
    const [validated, setValidated] = useState(false);

    const [archVoz, setArchVoz] = useState("");


    const [postulacion, setPostularme] = useState(false)

    let { url } = useParams();

    useEffect(() => {

        async function getCData() {

            //get concurso
            console.log(url);
            let resp = await fetch(`/api/concurso/${url}`)
            if (resp['status'] !== 200) {
                alert(resp['msg'])
                return
            }
            let data = await resp.json()
            setConcurso(data)
            setId(data.id)
            setImg(data.imagen)

            //get voces
        }
        getCData()
    }
        , [url])

    function subirPostulacion() {
        console.log("arriba los compas")
    }

    const handleSubmit = (event) => {
        const form = event.currentTarget;
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }else{
            subirPostulacion(); 
            setValidated(true);
        }
        
        
        
    };

    function concursoC() {

        const handleShow = () => setPostularme(true);
        const handleClose = () => setPostularme(false);

        if (Object.keys(concurso).length) {
            return (
                <div>
                    {/*Head*/}
                    <Navbar expand="lg" variant="dark" bg="dark">
                        <Container>
                            <Navbar.Brand >{concurso.nombre}</Navbar.Brand>
                        </Container>
                    </Navbar>

                    {/* BANNER */}
                    <div style={{ "textAlign": "center", "margin": "10px 0px" }}>
                        <Image src={imagen} alt="Banner" width="700"
                            height="350" />
                    </div>
                    {/* TABS */}
                    <div>
                        <Tabs
                            id="controlled-tab-example"
                            activeKey={key}
                            onSelect={(k) => setKey(k)}
                            className="mb-3"
                        >
                            <Tab eventKey="fechas" title="Fechas">
                                <b>Fecha de Inicio:</b> {concurso.fechaInicio.split("T")[0] + "/" + concurso.fechaInicio.split("T")[1]} | <b>Fecha de Fin:</b> {concurso.fechaFin.split("T")[0] + "/" + concurso.fechaFin.split("T")[1]}

                            </Tab>
                            <Tab eventKey="valor_a_pagar" title="Valor a Pagar">
                                <b>${concurso.valorPagar} COP</b>
                            </Tab>
                            <Tab eventKey="guion" title="Guión">
                                {concurso.guion}
                            </Tab>
                            <Tab eventKey="recomendaciones" title="Recomendaciones">
                                {concurso.recomendaciones}
                            </Tab>
                        </Tabs>
                    </div>
                    {/*Postularse*/}
                    <div>
                        <p></p>
                        <Button variant="secondary" onClick={handleShow}> Postularme </Button>
                        <p></p>
                    </div>
                    <Modal
                        show={postulacion}
                        onHide={handleClose}
                        backdrop="static"
                        keyboard={false}
                    >
                        <Modal.Header closeButton>
                            <Modal.Title>Detalles de la postulación:</Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <Form noValidate validated={validated} onSubmit={handleSubmit}>
                                <Form.Group className="mb-3" controlId="formBasicName">
                                    <Form.Label>Nombres</Form.Label>
                                    <Form.Control required type="text" placeholder="Ingrese su nombre" value={nombreE}
                                        onChange={evt => setNombreE(evt.target.value)} />
                                    <Form.Control.Feedback type="invalid">
                                        Esta campo es obligatorio.
                                    </Form.Control.Feedback>
                                </Form.Group>
                                <Form.Group className="mb-3" controlId="formBasicForName">
                                    <Form.Label>Apellidos</Form.Label>
                                    <Form.Control required type="text" placeholder="Ingrese sus apelllidos" value={apellidoE}
                                        onChange={evt => setApellidoE(evt.target.value)} />
                                    <Form.Control.Feedback type="invalid">
                                        Esta campo es obligatorio.
                                    </Form.Control.Feedback>
                                </Form.Group>
                                <Form.Group className="mb-3" controlId="formBasicEmail">
                                    <Form.Label>Email</Form.Label>
                                    <Form.Control required type="text" placeholder="Ingrese su email" value={emailE}
                                        onChange={evt => setEmailE(evt.target.value)} />
                                    <Form.Control.Feedback type="invalid">
                                        Ingrese su email.
                                    </Form.Control.Feedback>
                                </Form.Group>
                                <Form.Group controlId="formFile" className="mb-3">
                                    <Form.Label>Sube tu nota de voz</Form.Label>
                                    <Form.Control required type="file" onChange={evt => {
                                        var ext = evt.target.value.split('.').pop();
                                        ext = ext.toLowerCase();
                                        let vext = ['wav', 'mp3', 'aac', 'm4a', 'ogg'];
                                        if (vext.indexOf(ext) === -1) {
                                            alert("formato no valido de archivo")
                                            setArchVoz("")
                                        } else {
                                            setArchVoz(evt.target.value)
                                        }
                                    }} value={archVoz} />
                                    <Form.Control.Feedback type="invalid">
                                        Elija un archivo valido.
                                    </Form.Control.Feedback>
                                </Form.Group>
                                <Form.Group className="mb-3" controlId="formBasicObs">
                                    <Form.Label>Observaciones</Form.Label>
                                    <Form.Control type="text" placeholder="Ingrese sus observaciones" value={obs}
                                        onChange={evt => setObsE(evt.target.value)} />
                                </Form.Group>
                                <Button variant="primary" type="submit">
                                    Subir
                                </Button>
                            </Form>
                        </Modal.Body>
                    </Modal>
                   {/* AUDIOS */}
                   <Navbar expand="lg" bg="primary" variant="dark">
                        <Container>
                            <Navbar.Brand >Entradas</Navbar.Brand>
                        </Container>
                    </Navbar>

                                    
                </div>

            );
        } else {
            return (
                <div><p>No existe el concurso con esta URL</p></div>
            );
        }
    }
    return concursoC();
}
