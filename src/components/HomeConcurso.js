import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Typography } from '@mui/material';
import { useParams } from "react-router-dom";
import { CssBaseline } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({



}))
export default function HomeConcurso() {

    let { url } = useParams();
    
    function getCData() {
        //get url
        console.log(url);
        let resp =  fetch(`/api/url/${url}`).then();
        
    }


    function concurso() {
        getCData();
        return (
            <div>
                {/*Head*/}
                <Typography variant="h1" component="h2">Nombre del concurso</Typography>
                <p>HOLA</p>
            </div>
        );
    }
    return concurso();
}
