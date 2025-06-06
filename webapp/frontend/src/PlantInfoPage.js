
import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/brite/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Card, Tab, Tabs } from 'react-bootstrap';
import socket from './socket';
import { Line } from 'react-chartjs-2';
import { Button } from 'react-bootstrap';
import { Container, Nav, Navbar } from 'react-bootstrap';
import { Row, Col } from 'react-bootstrap';

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
  } from 'chart.js';
  
  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  );


const Header = () => {
const navigate = useNavigate();

return (
    <Navbar bg="primary" variant="light" expand="lg" className="mb-4">
    <Container>
        <Navbar.Brand href="/">
        <i className="bi bi-flower1 me-2"></i> 
        Sproutly
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="ms-auto">
            <Nav.Link onClick={() => navigate('/')} active>🌱 Home</Nav.Link>
            <Nav.Link onClick={() => navigate('/plant-info')}>👀 View Plants Details</Nav.Link>
            <Nav.Link onClick={() => navigate('/monitoring')}>📷 Live Camera</Nav.Link>
            <Nav.Link onClick={() => navigate('/control-command')}>🔌 Actuators</Nav.Link>
        </Nav>
        </Navbar.Collapse>
    </Container>
    </Navbar>
);
};

const PlantInfoPage = () => {

    const [numberOfPlants, setNumberOfPlants] = React.useState(null);

    const [selectedPlant, setSelectedPlant] = React.useState(null);  // default

    const [activeTab, setActiveTab] = React.useState('overview');

    React.useEffect(() => {
        if (!selectedPlant) {
            return;
        }

        console.log("Selected plant:", selectedPlant);

        fetch("https://172.26.192.48:8443/get-number-of-plants/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ plantId: selectedPlant.id })
        })
        .then(result => result.json())
        .then(data => {
            setNumberOfPlants(data.number_of_plants);
        }) 
        .catch(e => console.error("Failed to fetch number of plants", e));
    }, [selectedPlant]);

    const [plants, setPlants] = React.useState([]);
    
    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-user-plants/")
            .then(result => result.json())
            .then(data => {
                setPlants(data);
                if (data.length === 0) {
                    alert("Please add a plant first!");
                    navigate('/add-plant');
                    return;
                }
            })
            .catch(e => console.error("Failed to fetch user plants", e));
    }, []);


    const [currView, setCurrView] = React.useState('home'); // default

    React.useEffect(() => {
        if (!selectedPlant) {
            setSelectedPlant(plants[0]);
        }
    }, [plants]);

    const selectPlant = (plant) => {
        setSelectedPlant(plant);
        setCurrView('home');
    }



    const [plantInfo, setPlantInfo] = React.useState([]);

    React.useEffect(() => {
        if (!selectedPlant) {
            return;
        }

        fetch("https://172.26.192.48:8443/get-plant-info/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ species: selectedPlant.species })
        })
        .then(result => result.json())
        .then(data => {
            setPlantInfo(data);
        })
        .catch(e => console.error("Failed to fetch plant info", e));
    }, [selectedPlant]);



    // display 24 hours long of sensor data (sensor data is sent every 1 min)
    const [sensorDataHistory, setSensorDataHistory] = React.useState([]);


    React.useEffect(() => {
        if (!selectedPlant) {
            return;
        }

        console.log("Selected plant:", selectedPlant);
        fetch("https://172.26.192.48:8443/get-sensor-data-history/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ plantId: selectedPlant.id })
        })
            .then(res => res.json())
            .then(data => {
                console.log("Fetching past sensor data history:", data);
                setSensorDataHistory(data);
            })
            .catch(e => console.error("Failed to fetch sensor data history", e));
    }, [selectedPlant]);


    React.useEffect(() => {
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("data.type:", data.type);

            console.log("Sensor data chart update attempting...");

            const timestampedData = {
                ...data,
                timestamp: new Date().toLocaleString(),
            };

            // send notifications
            if (plantInfo) {
                const notifications = []
                if (data.temperature_f < plantInfo.temp_min) {
                    notifications.push('Temperature is too low :(');
                } else if (data.temperature_f > plantInfo.temp_max) {
                    notifications.push('Temperature is too high :(');
                }
                if (data.humidity < plantInfo.humidity_min) {
                    notifications.push('Humidity is too low :(');
                } else if (data.humidity > plantInfo.humidity_max) {
                    notifications.push('Humidity is too high :(');
                }
                // TODO: add more sensors
                if (notifications.length > 0) {
                    new Notification("Plant Health Alert!", {
                        body: `${notifications.join('\n')}`
                    });
                }
            }

            setSensorDataHistory((prevData) => 
                [...prevData.slice(-1439), timestampedData]
            );
            console.log("Sensor data chart updated!!!:", data);
        };

        // return () => socket.close();
        // TODO: idk why it's closing as soon as the page loads
    }, [selectedPlant, plantInfo]);
    


    const SensorChart = ({ label, dataKey, color }) => {
        const data = {
            labels: sensorDataHistory.map(d => d.timestamp),
            datasets: [
                {
                    label,
                    data: sensorDataHistory.map(d => d[dataKey]),
                    borderColor: color,
                    backgroundColor: color,
                }
            ]
        };
    
        const options = {
            responsive: true,
            plugins: {
                legend: { 
                    position: 'top',
                },
                title: { 
                    display: true, 
                    text: `${label}`, 
                }
            }
        };
    
        return <Line data={data} options={options} />;
    };
    
    let navigate = useNavigate();


    const deletePlant = async (e) => {
        e.preventDefault();

        if (window.confirm("Are you sure you want to delete this plant?")) {
            const deletePlantResponse = await fetch("https://172.26.192.48:8443/delete-plant/",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ plantId: selectedPlant.id }),
                }
            );
    
            const deletePlantResult = await deletePlantResponse.json();
            if (deletePlantResult.status === "Success") {
                alert("Successfully deleted plant!");
                navigate('/');
                return;
            } else if (deletePlantResult.status === "Error") {
                alert("Failed to delete plant.");
                navigate('/');
                return;
            }
        } else {
            return;
        }
    }

    const renderView = () => {
        if (!selectedPlant) {
            return (
                <div>
                    <h2>Loading...</h2>
                </div>
            )
        }
        return (
            <div>
                <Row>
                    <Col lg={4} className="mb-6">
                        <img src={selectedPlant.image_url} alt="Plant" width="200" height="200" />                                
                    </Col>

                    <Col lg={8}>
                            <Tabs
                                activeKey={activeTab}
                                onSelect={(k) => setActiveTab(k)}
                                className="mb-4"
                                >
                                <Tab 
                                    eventKey="overview" 
                                    title={
                                    <span>
                                        <i className="bi bi-grid-3x3-gap me-2"></i>
                                        Overview
                                    </span>
                                    }
                                >
                                    <Row>
                                    <Col md={6}>
                                        <SensorChart label="Temperature (°F)" dataKey="temperature_f" color="blue" />
                                    </Col>
                                    <Col md={6}>
                                        <SensorChart label="Humidity (%)" dataKey="humidity" color="green" />
                                    </Col>
                                    <Col md={6}>
                                        <SensorChart label="Soil Moisture (%)" dataKey="soil_moisture" color="purple" />
                                    </Col>
                                    <Col md={6}>
                                        <SensorChart label="Light (lux)" dataKey="lux" color="yellow" />
                                    </Col>
                                    </Row>
                                </Tab>
                                
                                <Tab 
                                    eventKey="temperature" 
                                    title={
                                    <span>
                                        <i className="bi bi-thermometer-half me-2"></i>
                                        Temperature
                                    </span>
                                    }
                                >
                                    <Row>
                                    <Col md={12}>
                                        <SensorChart label="Temperature (°F)" dataKey="temperature_f" color="blue" />
                                    </Col>
                                    <Col md={12}>
                                        <SensorChart label="Temperature (°C)" dataKey="temperature_c" color="red" />
                                    </Col>
                                    <Col md={12}>
                                        <SensorChart label="Soil Temperature (°C)" dataKey="soil_temp" color="pink" />
                                    </Col>
                                    </Row>
                                </Tab>
                                
                                <Tab 
                                    eventKey="moisture" 
                                    title={
                                    <span>
                                        <i className="bi bi-droplet-half me-2"></i>
                                        Moisture
                                    </span>
                                    }
                                >
                                    <Row>
                                    <Col md={12}>
                                        <SensorChart label="Humidity (%)" dataKey="humidity" color="green" />
                                    </Col>
                                    <Col md={12}>
                                        <SensorChart label="Soil Moisture (%)" dataKey="soil_moisture" color="purple" />
                                    </Col>
                                    </Row>
                                </Tab>
                                
                                <Tab 
                                    eventKey="nutrients" 
                                    title={
                                    <span>
                                        <i className="bi bi-flask me-2"></i>
                                        Nutrients
                                    </span>
                                    }
                                >
                                    <Row>
                                    <Col md={12}>
                                        <SensorChart label="pH" dataKey="ph" color="orange" />
                                    </Col>
                                    <Col md={6}>
                                        <SensorChart label="Nitrogen (mg/kg)" dataKey="nitrogen" color="teal" />
                                    </Col>
                                    <Col md={6}>
                                        <SensorChart label="Phosphorus (mg/kg)" dataKey="phosphorus" color="maroon" />
                                    </Col>
                                    <Col md={6}>
                                        <SensorChart label="Potassium (mg/kg)" dataKey="potassium" color="olive" />
                                    </Col>
                                    <Col md={6}>
                                        <SensorChart label="Conductivity (uS/cm)" dataKey="conductivity" color="brown" />
                                    </Col>
                                    </Row>
                                </Tab>
                                
                                <Tab 
                                    eventKey="light" 
                                    title={
                                    <span>
                                        <i className="bi bi-brightness-high me-2"></i>
                                        Light
                                    </span>
                                    }
                                >
                                    <Row>
                                    <Col md={12}>
                                        <SensorChart label="Light (lux)" dataKey="lux" color="yellow" />
                                    </Col>
                                    </Row>
                                </Tab>
                                </Tabs>
                    </Col>
                </Row>
            </div>
        );
    }


    return (
        <div className="home-page">
          <Header />
          <h1 className="mb-4">
            <i className="bi bi-info-circle-fill me-2 text-primary"></i>
            Plant Dashboard
        </h1>
            <div className="d-flex flex-wrap gap-3 justify-content-center mb-4">
                <Button variant="success" className="me-2" onClick={() => navigate('/add-plant')}>
                    <i className="bi bi-plus-circle me-2"></i>
                    ➕ Add New Plant
                </Button>
                <Button variant="danger" onClick={deletePlant}>
                    <i className="bi bi-trash me-2"></i>
                    🗑️ Delete Plant
                </Button>
            </div>

          <div className="d-flex justify-content-between align-items-center mb-3">
            <Tabs activeKey={selectedPlant ? selectedPlant.id.toString() : null} onSelect={(key) => {
                const plant = plants.find(p => p.id.toString() === key);
                if (plant) selectPlant(plant);
            }} className="flex-grow-1">
            {plants.map((plant) => (
            <Tab
                key={plant.id}
                eventKey={plant.id.toString()}
                title={
                    <span>
                        <i className="bi bi-flower1 me-2"></i>
                        {plant.name}
                    </span>}
            />
            ))}
            </Tabs>
          </div>
          {renderView()}

        </div>
      );
};


export default PlantInfoPage;