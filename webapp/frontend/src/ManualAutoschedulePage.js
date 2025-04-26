import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Form } from 'react-bootstrap';

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
    // let plantId = "";
    // if (!location.state) {
    //     plantId = 1;
    // } else {
    //     plantId = location.state.plantId;
    // }


    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-autoschedule/" + plantId)
            .then(result => result.json())
            .then(data => {
                console.log("Auto schedule fetched:", data);
                setMinTemp(data.minTemp);
                setMaxTemp(data.maxTemp);
                setMinHumidity(data.minHumidity);
                setMaxHumidity(data.maxHumidity);
                setLightStartTime(data.lightStartTime);
                setLightIntensity(data.lightIntensity);
                setLightHours(data.lightHours);
                setWaterFrequency(data.waterFrequency);
                setWaterStartTime(data.waterStartTime);
                setWaterAmount(data.waterAmount);
                setNutrientsStartTime(data.nutrientsStartTime);
                setNutrientsAmount(data.nutrientsAmount);
                setLoading(false);
            })
            .catch(e => console.error("Failed to fetch auto schedule", e));
    }, []);
      
    
    const submitManualAutoschedule = async (e) => {
        e.preventDefault();

        const scheduleSelected = { minTemp, maxTemp, minHumidity, maxHumidity, lightStartTime, lightIntensity, lightHours, waterFrequency, waterStartTime, waterAmount, nutrientsStartTime, nutrientsAmount };
        
        
        const response = await fetch("https://172.26.192.48:8443/manual-autoschedule/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ schedule: scheduleSelected, plantId: plantId, numberOfPlants: location.state.numberOfPlants }),
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


    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
          {loading ? (
            <div>Loading...</div>
          ) : (
            <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
                <h3>If you know your plant's ideal care conditions, you can set the schedule up manually here.</h3>
                <Form onSubmit={submitManualAutoschedule}>
                    <Form.Group className="mb-3">
                        <Form.Label>Minimum Temperature (°F)</Form.Label>
                        <Form.Control type="number" value={minTemp} onChange={(e) => setMinTemp(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Maximum Temperature (°F)</Form.Label>
                        <Form.Control type="number" value={maxTemp} onChange={(e) => setMaxTemp(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Minimum Humidity (%)</Form.Label>
                        <Form.Control type="number" value={minHumidity} onChange={(e) => setMinHumidity(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Maximum Humidity (%)</Form.Label>
                        <Form.Control type="number" value={maxHumidity} onChange={(e) => setMaxHumidity(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Light Start Time</Form.Label>
                        <Form.Control type="time" value={lightStartTime} onChange={(e) => setLightStartTime(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Light Intensity (Choose between 1~4)</Form.Label>
                        <Form.Control type="number" value={lightIntensity} onChange={(e) => setLightIntensity(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Light Duration (Hours)</Form.Label>
                        <Form.Control type="number" value={lightHours} onChange={(e) => setLightHours(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Water Frequency (Days)</Form.Label>
                        <Form.Control type="number" value={waterFrequency} onChange={(e) => setWaterFrequency(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Water Start Time</Form.Label>
                        <Form.Control type="time" value={waterStartTime} onChange={(e) => setWaterStartTime(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Water Amount per 1 Plant (mL)</Form.Label>
                        <Form.Control type="number" value={waterAmount} onChange={(e) => setWaterAmount(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Nutrients Start Time</Form.Label>
                        <Form.Control type="time" value={nutrientsStartTime} onChange={(e) => setNutrientsStartTime(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Nutrients Amount (mL per 100mL of water)</Form.Label>
                        <Form.Control type="number" value={nutrientsAmount} onChange={(e) => setNutrientsAmount(e.target.value)} required />
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
          )}
          
        </div>
      );
};


export default ManualAutoschedulePage;