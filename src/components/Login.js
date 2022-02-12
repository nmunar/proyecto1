import React, { useState } from 'react';

export default function Login(props){
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    function login(evt){
        evt.prebentDefault()
        if(!email.includes('@')){
            alert("Introduce a valid email")
            return
        }

        fetch('/login',{
            method: 'POST',
            body: JSON.stringify({
                email: email,
                contrasena: password
            }).then(resp => resp.json()).then(json=>{
                if(json["status_code"] == 401){
                    alert("The email or the password doesn't match")
                    return
                }
                localStorage.setItem("email", mail)
                localStorage.setItem("access_token", json["access_token"])
                props.setLogged(true)
                window.location.reload()
            }).cath(err =>{
                    alert('Failed login:'+err)
                })
        })

        return(
            <div>
                <form onSubmit={login}>
                <TextField
                    name="mail"
                    label="Correo"
                    id="mail"
                    value={mail}
                    onChange={evt => setEmail(evt.target.value)}
                />
                <TextField
                    name="password"
                    label="Contraseña"
                    type="password"
                    id="password"
                    autoComplete="current-password"
                    value={pass}
                    onChange={evt => setPassword(evt.target.value)}
                />
                <Button
                    type="submit"
                    fullWidth
                >
                    Entrar
                </Button>
            </form>
            </div>
        )
    }
}