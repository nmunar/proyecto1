import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import NavbarComp from "./components/NavbarComp";
import Profile from "./components/Profile";
import TableComp from "./components/TableComp";
import axios from "axios";
import { useState, useEffect } from "react";

function App() {
  const [isAuthenticatedApp, setAuthenticationApp] = useState(false);
  const [concursosList, setConcursosList] = useState([{}]);
  const [entra, setEntra] = useState(false);
  const [logged, setLogged] = useState(false);

  useEffect(() => {
    const access_token = localStorage.getItem("access_token")
    if(access_token)
      setLogged(true)
  },[])


  //Cambiar id del usuario
  const createConcurso = (
    nombre,
    imagen,
    fechaInicio,
    fechaFin,
    valorPagar,
    guion,
    recomendaciones
  ) => {
    let seconds = new Date().getTime() / 1000;
    let url =
      "http://127.0.0.1:5000/api/concursos/" +
      nombre.replace(/\s/g, "") +
      parseInt(seconds).toString();
    axios
      .post("http://127.0.0.1:5000/api/1/concursos", {
        nombre: nombre,
        imagen: imagen,
        url: url,
        fechaInicio: fechaInicio,
        fechaFin: fechaFin,
        valorPagar: valorPagar,
        guion: guion,
        recomendaciones: recomendaciones,
      })
      .then((response) => {
        let newConcursos = [...concursosList];
        newConcursos.unshift({
          id: response.data["id"],
          nombre: nombre,
          imagen: imagen,
          url: url,
          fechaCreacion: response.data["fechaCreacion"],
          fechaInicio: fechaInicio,
          fechaFin: fechaFin,
          valorPagar: valorPagar,
        });
        setConcursosList(newConcursos);
        alert("La URL pública de su concurso es: " + url);
      });
  };

  //Cambiar id del usuario
  const updateConcurso = (
    idC,
    nombre,
    imagen,
    fechaCreacion,
    fechaInicio,
    fechaFin,
    valorPagar,
    guion,
    recomendaciones
  ) => {
    axios
      .put("http://127.0.0.1:5000/api/1/concursos/" + idC, {
        nombre: nombre,
        imagen: imagen,
        fechaInicio: fechaInicio,
        fechaFin: fechaFin,
        valorPagar: valorPagar,
        guion: guion,
        recomendaciones: recomendaciones,
      })
      .then(() => {
        let newConcursos = [...concursosList];
        for (var i = 0; i < newConcursos.length; i++) {
          if (newConcursos[i].id == idC) {
            newConcursos[i] = {
              nombre: nombre,
              imagen: imagen,
              fechaCreacion: fechaCreacion,
              fechaInicio: fechaInicio,
              fechaFin: fechaFin,
              valorPagar: valorPagar,
              guion: guion,
              recomendaciones: recomendaciones,
            };
          }
        }
        setConcursosList(newConcursos);
      });
  };

  //Cambiar el id del usuario
  const deleteConcurso = (idC) => {
    axios.delete("/api/1/concursos/" + idC).then(() => {
      let newConcursos = [...concursosList];
      for (var i = 0; i < concursosList.length; i++) {
        if (concursosList[i].id == idC) {
          newConcursos.splice(i, 1);
        }
      }
      setConcursosList(newConcursos);
    });
  };

  if (isAuthenticatedApp) {
    if (entra == false) {
      setEntra(true);
      //Cambiar el id del usuario
      axios.get("/api/1/concursos").then((response) => {
        setConcursosList(response.data);
      });
    }
  }

  const changeAuthStatusLogin = (status) => {
    setAuthenticationApp(status);
  };

  return (
    <div className="App">
      <NavbarComp  logged = {logged} setLogged = {setLogged} funcAuth={changeAuthStatusLogin} />
      {isAuthenticatedApp ? (
        <>
          <Profile />
          <TableComp
            list={concursosList}
            funcCreate={createConcurso}
            funcUpdate={updateConcurso}
            funcDelete={deleteConcurso}
          />
        </>
      ) : (
        <></>
      )}
    </div>
  );
}

export default App;
