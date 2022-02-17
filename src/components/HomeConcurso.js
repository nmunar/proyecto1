import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Button,
  Tabs,
  Tab,
  Form,
  Container,
  Navbar,
  Row,
  Col,
  Modal,
  Image,
  ListGroup,
} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.css";
import ReactAudioPlayer from "react-audio-player";
import ReactPaginate from "react-paginate";

export default function HomeConcurso() {
  const [concurso, setConcurso] = useState({});
  const [idC, setId] = useState("");
  const [imagen, setImg] = useState("");
  const [nombreE, setNombreE] = useState("");
  const [apellidoE, setApellidoE] = useState("");
  const [emailE, setEmailE] = useState("");
  const [obs, setObsE] = useState("");
  const [key, setKey] = useState("home");
  const [validated, setValidated] = useState(false);
  const [archVoz, setArchVoz] = useState({});
  const [postulacion, setPostularme] = useState(false);
  
  const [audios, setAudios] = useState([]);//--------
  const [currentPage, setCurrentPage] = useState(1);
  const [postsPerPage, setPostsPerPage] = useState(20);

  const indexOfLastPost = currentPage*postsPerPage;
  const indexOfFirstPost = indexOfLastPost-postsPerPage;
  const currentPosts = audios.slice(indexOfFirstPost,indexOfLastPost);

  const paginate = (number) => {
    setCurrentPage(number+1)
  }

  
  const [hizoFecth, setFecth] = useState(false);

  let { url } = useParams();

  useEffect(() => {
    async function getCData() {
      //get concurso
      let res = await fetch(`http://127.0.0.1:5000/api/concurso/${url}`);
      let data = await res.json();

      if (res["status"] !== 200) {
        alert(data["msg"]);
        return;
      }

      setConcurso(data);
      setId(data.id);
      setImg(data.imagen);

      //get voces
      let resp = await fetch(`http://127.0.0.1:5000/api/voces/${data.id}`);
      let json = await resp.json();

      if (resp["status"] !== 200) {
        alert(json["msg"]);
        return;
      }

      console.log(json);
      const vocesF = json["voces"];
      //archvivos convertidos
      let audios = [];
      for (let voz of vocesF) {
        console.log(voz);
        let respon = await fetch(`http://127.0.0.1:5000/api/audio/${voz.id}?convertido=1`);
        let respblob = await respon.blob();
        let fechC = voz.fechaCreacion.split("T");
        audios.push({
          id: voz.id,
          nombres: voz.nombres,
          apellidos: voz.apellidos,
          email: voz.email,
          obs: voz.observaciones,
          fecha: fechC[0] + " Hora : " + fechC[1].split(".")[0],
          url: respblob,
        });
      }

      console.log(audios);
      setAudios(audios);
      setFecth(true);
    }
    getCData();
  }, []);

  if (validated) {
    subirPostulacion();
  }

  function cargarAudios() {
    if (audios.length && hizoFecth) {
      return (
        <>
          <Container>
            <ListGroup>
              {currentPosts.map((obj, index) => {
                return (
                  <>
                    <ListGroup.Item key={obj.id}>
                      <Row key={obj.id + "a"}>
                        <p>
                          <b>Subido:</b> {obj.fecha} - <b>Nombre:</b>{" "}
                          {obj.nombres + " " + obj.apellidos} -- <b>Email: </b>
                          {obj.email}
                        </p>
                        {obj.obs !== "" ? (
                          <p>
                            Observaciones: <i>{obj.obs}</i>
                          </p>
                        ) : (
                          <></>
                        )}
                      </Row>
                      <Row key={obj.id + "b"}>
                        <ReactAudioPlayer
                          src={URL.createObjectURL(obj.url)}
                          controls
                          key={obj.id + "c"}
                        />
                      </Row>
                    </ListGroup.Item>
                  </>
                );
              })}
            </ListGroup>
            <ReactPaginate
            previousLabel={"<"}
            nextLabel={">"}
            breakLabel={"..."}
            pageCount={Math.ceil(audios.length/postsPerPage)}
            onPageChange={handlePageClick}
            containerClassName={"pagination justify-content-center"}
            pageClassName={"page-item"}
            pageLinkClassName={"page-link"}
            previousClassName={"page-item"}
            previousLinkClassName={"page-link"}
            nextClassName={"page-item"}
            nextLinkClassName={"page-link"}
            breakClassName={"page-item"}
            breakLinkClassName={"page-link"}
            activeClassName={"active"}
          />
          </Container>
        </>
      );
    } else if (!audios.length && hizoFecth) {
      return (
        <>
          <p>Actualmente se esan cargando lo audios</p>
        </>
      );
    } else {
      return (
        <>
          <p>La posulacion está vacía</p>
        </>
      );
    }
  }

  const handlePageClick = (event) => {
    paginate(event.selected);
    
  };

  async function subirPostulacion() {
    // fetch envio audio
    var data = new FormData();
    data.append("file", archVoz);
    console.log(data);
    console.log(archVoz);
    const response = await fetch("http://127.0.0.1:5000/api/audio", {
      method: "POST",
      body: data,
    });

    const json = await response.json();

    console.log(json);

    const data2 = {
      email: emailE,
      nombres: nombreE,
      apellidos: apellidoE,
      observaciones: obs,
      concursoId: idC,
      archivoId: json.id,
    };

    const res = await fetch("http://127.0.0.1:5000/api/voz", {
      method: "POST",
      body: JSON.stringify(data2),
    });
    console.log(res["status"]);
    if (res["status"] !== 201) {
      alert("No se pudo completar la postuación");
      setPostularme(false);
      return;
    }
    const json2 = await res.json();
    console.log(json2);
    alert(
      "Hemos recibido tu voz y la estamos procesando para que sea publicada en la página del concurso y pueda ser posteriormente revisada por nuestro equipo de trabajo."
    );
    setEmailE("");
    setNombreE("");
    setApellidoE("");
    setPostularme(false);
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    if (nombreE == "" || apellidoE == "" || emailE == "" || archVoz == "") {
      alert("Debe completar todos los campos.");
    } else {
      subirPostulacion();
      setPostularme(false);
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
              <Navbar.Brand>{concurso.nombre}</Navbar.Brand>
            </Container>
          </Navbar>

          {/* BANNER */}
          <div style={{ textAlign: "center", margin: "10px 0px" }}>
            <Image src={imagen} alt="Banner" width="700" height="350" />
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
                <b>Fecha de Inicio:</b>{" "}
                {concurso.fechaInicio.split("T")[0] +
                  "/" +
                  concurso.fechaInicio.split("T")[1]}{" "}
                | <b>Fecha de Fin:</b>{" "}
                {concurso.fechaFin.split("T")[0] +
                  "/" +
                  concurso.fechaFin.split("T")[1]}
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
            <Button variant="secondary" onClick={handleShow}>
              {" "}
              Postularme{" "}
            </Button>
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
              <Form>
                <Form.Group className="mb-3" controlId="formBasicName">
                  <Form.Label>Nombres</Form.Label>
                  <Form.Control
                    required
                    type="text"
                    placeholder="Ingrese su nombre"
                    value={nombreE}
                    onChange={(evt) => setNombreE(evt.target.value)}
                  />
                </Form.Group>
                <Form.Group className="mb-3" controlId="formBasicForName">
                  <Form.Label>Apellidos</Form.Label>
                  <Form.Control
                    required
                    type="text"
                    placeholder="Ingrese sus apelllidos"
                    value={apellidoE}
                    onChange={(evt) => setApellidoE(evt.target.value)}
                  />
                </Form.Group>
                <Form.Group className="mb-3" controlId="formBasicEmail">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    required
                    type="text"
                    placeholder="Ingrese su email"
                    value={emailE}
                    onChange={(evt) => setEmailE(evt.target.value)}
                  />
                </Form.Group>
                <Form.Group controlId="formFile" className="mb-3">
                  <Form.Label>Sube tu nota de voz</Form.Label>
                  <Form.Control
                    required
                    type="file"
                    onChange={(evt) => {
                      var ext = evt.target.value.split(".").pop();
                      ext = ext.toLowerCase();
                      let vext = ["wav", "mp3", "aac", "ogg"];

                      if (vext.indexOf(ext) === -1) {
                        alert("formato no valido de archivo");
                        setArchVoz("");
                      } else {
                        setArchVoz(evt.target.files[0]);
                      }
                    }}
                  />
                </Form.Group>
                <Form.Group className="mb-3" controlId="formBasicObs">
                  <Form.Label>Observaciones</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Ingrese sus observaciones"
                    value={obs}
                    onChange={(evt) => setObsE(evt.target.value)}
                  />
                </Form.Group>
                <Button variant="primary" type="submit" onClick={handleSubmit}>
                  Subir
                </Button>
              </Form>
            </Modal.Body>
          </Modal>
          {/* AUDIOS */}
          <Navbar expand="lg" bg="primary" variant="dark">
            <Container>
              <Navbar.Brand>Entradas</Navbar.Brand>
            </Container>
          </Navbar>
          <Container>
            <p></p>
            {cargarAudios()}
          </Container>
        </div>
      );
    } else {
      return (
        <div>
          <p>No existe el concurso con esta URL</p>
        </div>
      );
    }
  }
  return concursoC();
}
