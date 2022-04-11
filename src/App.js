import "bootstrap/dist/css/bootstrap.min.css";
import NavbarComp from "./components/NavbarComp";
import Profile from "./components/Profile";
import TableComp from "./components/TableComp";
import HomeConcurso from "./components/HomeConcurso";
import { makeStyles } from "@material-ui/core/styles";
import axios from "axios";
import { useState, useEffect } from "react";
import Descripcion from "./components/Descripcion";
import ReactPaginate from "react-paginate";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

const useStyles = makeStyles((theme) => ({
  app: {
    textAlign: "center",
  },
}));

function App() {
  const [concursosList, setConcursosList] = useState([{}]);
  const [entra, setEntra] = useState(false);
  const [logged, setLogged] = useState(false);

  const classes = useStyles();

  const [currentPage, setCurrentPage] = useState(1);
  const [postsPerPage, setPostsPerPage] = useState(20);

  const indexOfLastPost = currentPage * postsPerPage;
  const indexOfFirstPost = indexOfLastPost - postsPerPage;
  const currentPosts = concursosList.slice(indexOfFirstPost, indexOfLastPost);

  const paginate = (number) => {
    setCurrentPage(number + 1);
  };

  const [urlPath, setUrl] = useState(window.location.pathname);

  useEffect(() => {
    const access_token = localStorage.getItem("access_token");
    if (access_token) setLogged(true);
    setUrl(window.location.pathname);
  }, []);

  //Cambiar id del usuario
  const createConcurso = (
    nombre,
    imagen,
    fechaInicio,
    fechaFin,
    valorPagar,
    url,
    guion,
    recomendaciones
  ) => {
    //let seconds = new Date().getTime() / 1000;
    //let url = nombre.replace(/\s/g, "") + parseInt(seconds).toString();
    axios
      .post(
        "/api/concursos",
        {
          nombre: nombre,
          imagen: imagen,
          url: url,
          fechaInicio: fechaInicio,
          fechaFin: fechaFin,
          valorPagar: valorPagar,
          guion: guion,
          recomendaciones: recomendaciones,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      )
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
        // alert(
        //   "La URL pública de su concurso es: " +
        //     "http://127.0.0.1:3000/home/concurso/" +
        //     url
        // );
        window.location.reload();
      })
      .catch((err) => {
        if (err === "Error: Request failed with status code 403") {
          alert(
            "El path de la URL del concurso ya está en uso. Por favor asigne una distinta."
          );
        }
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
    url,
    guion,
    recomendaciones
  ) => {
    axios
      .put(
        "/api/concursos/" + idC,
        {
          nombre: nombre,
          imagen: imagen,
          fechaInicio: fechaInicio,
          fechaFin: fechaFin,
          valorPagar: valorPagar,
          url: url,
          guion: guion,
          recomendaciones: recomendaciones,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      )
      .then(() => {
        let newConcursos = [...concursosList];
        for (var i = 0; i < newConcursos.length; i++) {
          if (newConcursos[i].id === idC) {
            newConcursos[i] = {
              nombre: nombre,
              imagen: imagen,
              fechaCreacion: fechaCreacion,
              fechaInicio: fechaInicio,
              fechaFin: fechaFin,
              valorPagar: valorPagar,
              url: url,
              guion: guion,
              recomendaciones: recomendaciones,
            };
          }
        }
        setConcursosList(newConcursos);
        window.location.reload();
      })
      .catch((err) => {
        if (err === "Error: Request failed with status code 403") {
          alert(
            "El path de la URL del concurso a actualizar ya está en uso. Por favor asigne una distinta."
          );
        }
      });
  };

  //Cambiar el id del usuario
  const deleteConcurso = (idC) => {
    axios
      .delete("/api/concursos/" + idC, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      .then(() => {
        let newConcursos = [...concursosList];
        for (var i = 0; i < concursosList.length; i++) {
          if (concursosList[i].id === idC) {
            newConcursos.splice(i, 1);
          }
        }
        setConcursosList(newConcursos);
      });
  };

  if (logged) {
    if (entra === false) {
      setEntra(true);
      //Cambiar el id del usuario
      axios
        .get("/api/concursos", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        })
        .then((response) => {
          setConcursosList(response.data);
        });
    }
  }

  const handlePageClick = (event) => {
    paginate(event.selected);
  };

  return (
    <div className={classes.app}>
      {!urlPath.includes("home") ? (
        <>
          <NavbarComp logged={logged} setLogged={setLogged} />
          {logged ? (
            <>
              <Profile />
              <TableComp
                list={currentPosts}
                funcCreate={createConcurso}
                funcUpdate={updateConcurso}
                funcDelete={deleteConcurso}
              />
              <ReactPaginate
                previousLabel={"<"}
                nextLabel={">"}
                breakLabel={"..."}
                pageCount={Math.ceil(concursosList.length / postsPerPage)}
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
            </>
          ) : (
            <>
              <div style={{ backgroundColor: "rgb(236, 226, 198)" }}>
                <Descripcion />
              </div>
            </>
          )}
        </>
      ) : (
        <>
          <Router>
            <Routes>
              {/*Home Concursos*/}
              <Route
                path="/home/concurso/:url"
                element={<HomeConcurso />}
              ></Route>
            </Routes>
          </Router>
        </>
      )}
    </div>
  );
}

export default App;
