import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/brite/bootstrap.min.css';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Form, Alert } from 'react-bootstrap';
import { Container, Nav, Navbar } from 'react-bootstrap';

const ManualAutoschedulePage = () => {

    const [loading, setLoading] = React.useState(true);
    const [minTemp, setMinTemp] = React.useState('');
    const [maxTemp, setMaxTemp] = React.useState('');
    const [minHumidity, setMinHumidity] = React.useState('');
    const [maxHumidity, setMaxHumidity] = React.useState('');
    const [lightStartTime, setLightStartTime] = React.useState('');
    const [lightIntensity, setLightIntensity] = React.useState(''); // 1~4
    const [lightHours, setLightHours] = React.useState(''); // how long the light is on
    const [waterFrequency, setWaterFrequency] = React.useState(''); // every xx hours
    const [waterStartTime, setWaterStartTime] = React.useState('');
    const [waterAmount, setWaterAmount] = React.useState(''); // how much water to give
    const [nutrientsStartTime, setNutrientsStartTime] = React.useState('');
    const [nutrientsAmount, setNutrientsAmount] = React.useState('');

    let navigate = useNavigate();
    let location = useLocation();
    let plantId = location.state.plantId;
    let plantSpecies = location.state.plantSpecies;


    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-autoschedule/" + plantId)
            .then(result => result.json())
            .then(data => {
                console.log("Auto schedule fetched:", data);
                setMinTemp(data.min_temp?.toString() || '');
                setMaxTemp(data.max_temp?.toString() || '');
                setMinHumidity(data.min_humidity?.toString() || '');
                setMaxHumidity(data.max_humidity?.toString() || '');
                setLightStartTime(data.light_start_time?.toString() || '');
                setLightIntensity(data.light_intensity?.toString() || '');
                setLightHours(data.light_hours?.toString() || '');
                setWaterFrequency(data.water_frequency?.toString() || '');
                setWaterStartTime(data.water_start_time?.toString() || '');
                setWaterAmount(data.water_amount?.toString() || '');
                setNutrientsStartTime(data.nutrients_start_time?.toString() || '');
                setNutrientsAmount(data.nutrients_amount?.toString() || '');
                setLoading(false);
            })
            .catch(e => console.error("Failed to fetch auto schedule", e));
    }, [plantId]);
      
    
    const submitManualAutoschedule = async (e) => {
        e.preventDefault();

        if (parseFloat(minTemp) > parseFloat(maxTemp)) {
            alert("Minimum temperature must be less than maximum temperature.");
            return;
        }
        if (parseFloat(minHumidity) > parseFloat(maxHumidity)) {
            alert("Minimum humidity must be less than maximum humidity.");
            return;
        }

        const scheduleSelected = { minTemp, maxTemp, minHumidity, maxHumidity, lightStartTime, lightIntensity, lightHours, waterFrequency, waterStartTime, waterAmount, nutrientsStartTime, nutrientsAmount };
        
        console.log("number of plants", location.state.numberOfPlants);

        const response = await fetch("https://172.26.192.48:8443/manual-autoschedule/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ schedule: scheduleSelected, plantId: plantId, numberOfPlants: location.state?.numberOfPlants || 1 }),
            }
        );

        const result = await response.json();
        if (result.status === "Success") {
            alert("Successfully added/updated your plant's schedule!");
            navigate('/');
        } else if (result.status === "Error") {
            alert("Failed to add/update your plant's schedule.");
        }
    };

    const [plantInfo, setPlantInfo] = React.useState([]);
    
    React.useEffect(() => {

        fetch("https://172.26.192.48:8443/get-plant-info/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ species: plantSpecies })
        })
        .then(result => result.json())
        .then(data => {
            setPlantInfo(data);
        })
        .catch(e => console.error("Failed to fetch plant info", e));
    }, []);


    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
          {loading ? (
            <div>Loading...</div>
          ) : (
            <div className="min-vh-100">
                
                <div className="row">
                    <div className="col-md-4 mb-4">
                        <div className="card">
                            <div className="card-body">
                                {plantInfo ? (
                                    <>
                                        <h5 className="card-title">Ideal Care Conditions</h5>
                                        <p><strong>Minimum Temperature:</strong> {plantInfo.temp_min}°F</p>
                                        <p><strong>Maximum Temperature:</strong> {plantInfo.temp_max}°F</p>
                                        <p><strong>Minimum Humidity:</strong> {plantInfo.humidity_min}%</p>
                                        <p><strong>Maximum Humidity:</strong> {plantInfo.humidity_max}%</p>
                                        <p><strong>Light Intensity:</strong> {plantInfo.light_intensity} lux</p>
                                        <p><strong>Info about Lighting:</strong> {plantInfo.light_description} hours</p>
                                        <p><strong>Info about Watering:</strong> {plantInfo.water_description}</p>
                                        <p><strong>Minimum pH:</strong> {plantInfo.ph_min}</p>
                                        <p><strong>Maximum pH:</strong> {plantInfo.ph_max}</p>
                                    </>
                                ) : (
                                    <Alert variant="info">No specific care information available for this plant.</Alert>
                                )}
                                
                            </div>
                        </div>
                    </div>

                    <div className="col-md-8">
                        <Form onSubmit={submitManualAutoschedule}>
                            <Form.Group className="mb-3">
                                <Form.Label>Minimum Temperature (°F)</Form.Label>
                                <Form.Control type="number" value={minTemp} onChange={(e) => setMinTemp(e.target.value)} min={45} max={85} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Maximum Temperature (°F)</Form.Label>
                                <Form.Control type="number" value={maxTemp} onChange={(e) => setMaxTemp(e.target.value)} min={50} max={90} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Minimum Humidity (%)</Form.Label>
                                <Form.Control type="number" value={minHumidity} onChange={(e) => setMinHumidity(e.target.value)} min={0} max={100} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Maximum Humidity (%)</Form.Label>
                                <Form.Control type="number" value={maxHumidity} onChange={(e) => setMaxHumidity(e.target.value)} min={0} max={100}required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Light Start Time</Form.Label>
                                <Form.Control type="time" value={lightStartTime} onChange={(e) => setLightStartTime(e.target.value)} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Light Intensity (Choose between 1~4)</Form.Label>
                                <Form.Control type="number" value={lightIntensity} onChange={(e) => setLightIntensity(e.target.value)} min={1} max={4} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Light Duration (Hours)</Form.Label>
                                <Form.Control type="number" value={lightHours} onChange={(e) => setLightHours(e.target.value)} min={1} max={24} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Water Frequency (Days)</Form.Label>
                                <Form.Control type="number" value={waterFrequency} onChange={(e) => setWaterFrequency(e.target.value)} min={1} max={60} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Water Start Time</Form.Label>
                                <Form.Control type="time" value={waterStartTime} onChange={(e) => setWaterStartTime(e.target.value)} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Water Amount per 1 Plant (mL)</Form.Label>
                                <Form.Control type="number" value={waterAmount} onChange={(e) => setWaterAmount(e.target.value)} min={5} max={2000} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Nutrients Start Time</Form.Label>
                                <Form.Control type="time" value={nutrientsStartTime} onChange={(e) => setNutrientsStartTime(e.target.value)} required />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Nutrients Amount (mL per 100mL of water)</Form.Label>
                                <Form.Control type="number" value={nutrientsAmount} onChange={(e) => setNutrientsAmount(e.target.value)} min={0} max={20} required />
                            </Form.Group>
                            <Button variant="primary" type="submit">
                                Set up Auto-Schedule
                            </Button>
                        </Form>
                    </div>
                </div>


                <div className="d-flex justify-content-center mb-4">
                    <Button onClick={() => navigate('/')}>
                        <i className="bi bi-arrow-left"></i>
                        Back to Home
                    </Button>
                </div>

            </div>
          )}
          
        </div>
      );
};


export default ManualAutoschedulePage;