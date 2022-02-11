import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Typography } from '@mui/material';
import { CssBaseline } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({



}))
export default function HomeConcurso({ match }) {

    function concurso() {

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
