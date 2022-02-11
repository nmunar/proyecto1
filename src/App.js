import './App.css';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";
import HomeConcurso from './components/HomeConcurso';

function App() {

  return (
    <Router>
      <Routes>
        {/*Home Concursos*/}
        <Route path="/home/concurso/:url" element={<HomeConcurso />}></Route>
      </Routes>
    </Router>
  );
}

export default App;
