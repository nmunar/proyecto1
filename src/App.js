import logo from './logo.svg';
import './App.css';
import NavigationBar from './components/NavBar';
import React, { useState, useEffect } from 'react';

function App() {
  const [logged, setLogged] = useState(false)

  useEffect(() => {
    const access_token = localStorage.getItem("access_token")
    if(access_token)
      setLogged(true)
  },[])


  return (
    <div>
      <NavigationBar
        logged = {logged}
        setLogged = {setLogged}
      />
      <header >
        
      </header>
    </div>
  );
}

export default App;
