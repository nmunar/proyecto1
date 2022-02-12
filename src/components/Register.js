import React, { useState } from 'react';

export default function Register(props){

    const [nombre, setNombre] = useState("")    
    const [apellido, setApellido] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")

    function register(evt){
        evt.preventDefault()

        if(!mail.includes('@')){
            alert("Introduce a valid email")
            return
        }
        if(password != confirmPassword){
            alert("The passwords don't match")
            return
        }

        fetch('api/register',{
            method:"POST",
            body: JSON.stringfy({
                nombres: pNombre,
                apellidos: pApellido,
                email: pEmail,
                contrasena: pPassword
            })
        }).then(resp=>{
            if(resp["status"] === 400){
                alert("The email is already used")
            }else{
                return resp.json()
            }
        }).then(json => {
            if(json === undefined)
                return
            props.setOpen(false)
        }).catch(err => {
            alert('Bad sign up : '+err)
        })
    }

    return(
        <form onSubmit={register}>
            <TextField
                    name="nombre"
                    id="nombre"
                    label="Nombres"
                    value={nombre}
                    onChange={evt => setNombre(evt.target.value)}
                />
            <TextField
                    name="apellido"
                    id="apellido"
                    label="Apellidos"
                    value={apellido}
                    onChange={evt => setApellido(evt.target.value)}
                />
            <TextField
                    name="email"
                    id="email"
                    label="Correo"
                    value={email}
                    onChange={evt => setEmail(evt.target.value)}
                />
            <TextField
                    name="password"
                    id="password"
                    label="Contraseña"
                    value={password}
                    onChange={evt => setPassword(evt.target.value)}
                />
            <TextField
                    name="confirmPassword"
                    id="confirmPassword"
                    label="Verificar contraseña"
                    value={confirmPassword}
                    onChange={evt => setConfirmPassword(evt.target.value)}
                />
        </form>
    )
        
}