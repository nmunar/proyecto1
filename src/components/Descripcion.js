import React, { useState } from 'react';
import "bootstrap/dist/css/bootstrap.min.css";
import "./Descripcion.css";
import { Button, Container } from "react-bootstrap";
import Register from './Register';

export default function Descripcion(){

    return(<>
        <Container>
            <figure className="position-relative">
                <img src="https://www.eleconomista.com.mx/__export/1522095578091/sites/eleconomista/img/2018/03/26/cabina-radio-_-archivo.jpg_554688468.jpg" className='img-fluid'/>
                <figcaption>
                    <h1 className="titulo">SuperVoices</h1>
                    <h3>Queremos encontrar tu voz</h3>
                </figcaption>
            </figure>
            <div className="row">
                <div className="col-4">
                    <h2 className="super">¿Qué es SuperVoices?</h2>
                </div>
                <div className="col-8">
                    <div className="informacion">
                        <p>Somos una compañia que ofrece a todo tipo de empresas la facilidad de encontrar las mejores voces para todo tipo de anuncios publicitarios.</p>
                        <p>Ofrecemos un software como servicio (SaaS) con el fin de librar una plataforma en la nube en la cual se pueden crear un concurso
                            con el fin de buscar un locutor para cualquie espacio, como un video de YouTube, un comercial de televisión o radio entre otros.</p>
                        <p>Lo mejor es que es fácil de usar para los participantes, los cuales pueden ver la lista de concursos activos y enviar su participación sin tener
                            que crear una cuenta. Y para empezar a utilizar nuestro servicio solo necesitas registrarte. ¿Qué esperas?
                        </p>
                    </div>                    
                    <Register />
                </div>
            </div>
        </Container>
    </>)
}
