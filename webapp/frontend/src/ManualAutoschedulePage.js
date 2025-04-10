import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Form } from 'react-bootstrap';

const ManualAutoschedulePage = () => {

    const [minTemp, setMinTemp] = React.useState('');
    const [maxTemp, setMaxTemp] = React.useState('');
    const [minHumidity, setMinHumidity] = React.useState('');
    const [maxHumidity, setMaxHumidity] = React.useState('');
    const [lightFrequency, setLightFrequency] = React.useState(''); // every xx hours
    const [lightHours, setLightHours] = React.useState(''); // how long the light is on
    const [waterFrequency, setWaterFrequency] = React.useState(''); // every xx hours
    const [waterAmount, setWaterAmount] = React.useState(''); // how much water to give
    // add other sensors later (nutrients, etc.)

    let navigate = useNavigate();
    let location = useLocation();
    let plantId = "";
    if (!location.state) {
        plantId = 0;
    } else {
        plantId = location.state.plantId;
    }
      
    
    const submitManualAutoschedule = async (e) => {
        e.preventDefault();

        const scheduleSelected = { minTemp, maxTemp, minHumidity, maxHumidity, lightFrequency, lightHours, waterFrequency, waterAmount };
        
        
        const response = await fetch("https://172.26.192.48:8443/manual-autoschedule/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ schedule: scheduleSelected, plantId: plantId }),
            }
        );

        const result = await response.json();
        if (result.status === "Success") {
            alert("Successfully added/updated your plant's schedule!");
        } else if (result.status === "Error") {
            alert("Failed to add/update your plant's schedule.");
        }
    };


    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
            <h3>If you know your plant's ideal care conditions, you can set the schedule up manually here.</h3>
            <Form onSubmit={submitManualAutoschedule}>
                <Form.Group className="mb-3">
                    <Form.Label>Minimum Temperature (°F)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setMinTemp(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Maximum Temperature (°F)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setMaxTemp(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Minimum Humidity (%)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setMinHumidity(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Maximum Humidity (%)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setMaxHumidity(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Light Frequency (Hours)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setLightFrequency(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Light Duration (Hours)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setLightHours(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Water Frequency (Hours)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setWaterFrequency(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Water Amount (mL)</Form.Label>
                    <Form.Control type="number" onChange={(e) => setWaterAmount(e.target.value)} required />
                </Form.Group>
                <Button variant="primary" type="submit">
                    Set up Auto-Schedule
                </Button>
            </Form>

            <div className="d-flex justify-content-center mb-4">
                <Button onClick={() => navigate('/')}>
                    <i className="bi bi-arrow-left"></i>
                    Back to Home
                </Button>
            </div>

          </div>
        </div>
      );
};


export default ManualAutoschedulePage;