
import './App.css';
import React, { useState } from "react"; 
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import { Login } from './components/Login'
import { ProjectList } from './components/ProjectList';
import { SentenceList } from './components/SentenceList';


function App() {
  
  return (
    <div className="App">
      {
        <Router>
          <Routes>
            <Route path='/login' element={<Login />} />
            <Route path='/' element={<ProjectList />} />
            {/* :projectId is a path param */}
            <Route path='/project/:projectId' element={<SentenceList />} />
          </Routes>
        </Router>
      }
    </div>
  );
}

export default App;
