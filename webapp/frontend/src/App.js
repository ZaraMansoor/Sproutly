/**
 * References:
 * https://v5.reactrouter.com/web/example/basic
 */

import './App.css';

import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/brite/bootstrap.min.css';


import HomePage from './HomePage';
import MonitoringPage from './MonitoringPage';
import AddPlantPage from './AddPlantPage';
import ControlCommandPage from './ControlCommandPage';
import ManualAutoschedulePage from './ManualAutoschedulePage';
import DetectionResultPage from './DetectionResultPage';
import PlantInfoPage from './PlantInfoPage';

function App() {
  return (
    <Router>
      <div className="App">
        <div className="container mt-4">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/add-plant" element={<AddPlantPage />} />
            <Route path="/detection-result" element={<DetectionResultPage />} />
            <Route path="/manual-autoschedule" element={<ManualAutoschedulePage />} />
            <Route path="/control-command" element={<ControlCommandPage />} />
            <Route path="/plant-info" element={<PlantInfoPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}


export default App;
