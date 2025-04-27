/**
 * References:
 * https://react.dev/learn
 * https://react-chartjs-2.js.org/examples/line-chart
 * https://react-bootstrap.netlify.app/docs/components/tabs
 * https://developer.chrome.com/docs/extensions/reference/api/notifications
 * https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API
 */

import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/brite/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Tab, Tabs } from 'react-bootstrap';
import socket from './socket';
import { Line } from 'react-chartjs-2';
import { Form } from 'react-bootstrap';
import { Button } from 'react-bootstrap';
import { Card } from 'react-bootstrap';

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

const HomePage = () => {

    const [numberOfPlants, setNumberOfPlants] = React.useState(null);

    const [selectedCurrPlantId, setSelectedCurrPlantId] = React.useState(null);
    const [selectedNumberOfPlants, setSelectedNumberOfPlants] = React.useState(null);


    const [currView, setCurrView] = React.useState('home'); // default


    const fetchCurrentPlant = () => {
        fetch("https://172.26.192.48:8443/get-current-plant/")
            .then(result => result.json())
            .then(data => {
                setCurrPlantName(data.current_plant_name);
            })
            .catch(e => console.error("Failed to fetch current plant", e));
    };

    React.useEffect(() => {
        fetchCurrentPlant();
    }, []);

    const [plantHealth, setPlantHealth] = React.useState([]);

    const [lastDetected, setLastDetected] = React.useState([]);

    const listenForHealthCheck = () => {
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("data.type:", data.type);
            if (data.type === "plant_health") {
                if (selectedPlant && data.status === "Healthy") {
                    new Notification("Plant Health Alert!", {
                        body: `Plant ${selectedPlant.name} is healthy! yay :)`
                    });
                    setPlantHealth("Healthy");
                    setLastDetected(data.time);
                    return;
                }
                if (selectedPlant && data.status === "Unhealthy") {
                    new Notification("Plant Health Alert!", {
                        body: `Plant ${selectedPlant.name} is unhealthy!`
                    });
                    setPlantHealth("Unhealthy");
                    setLastDetected(data.time);
                    return;
                }
            }
        };
    };
    
    


    const sendCommand = async (commandData) => {
        try {
            const response = await fetch("https://172.26.192.48:8443/send-command/",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(commandData),
                });
            console.log("Control command sent", await response.json());
        } catch (error) {
            console.error("Error sending control command:", error);
        }
    }

    const automaticOrManual = async (choice) => {
        try {
            const response = await fetch("https://172.26.192.48:8443/automatic-or-manual/",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(choice),
                });
            console.log("automatic or manual sent", await response.json());
        } catch (error) {
            console.error("Error sending automatic or manual:", error);
        }
    }

    let navigate = useNavigate();

    const [automaticMode, setAutomaticMode] = React.useState(null);

    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-automatic-or-manual/")
            .then(result => result.json())
            .then(data => {
                console.log("Automatic or Manual fetched!!:", data);
                setAutomaticMode(data["automatic_or_manual"]);
            })
            .catch(e => console.error("Failed to fetch automatic or manual", e));
    }, [])


    const submitNumberOfPlants = async (e) => {
        e.preventDefault();

        if (!numberOfPlants) {
            alert("error with number of plants");
            return;
        }

        const numberOfPlantsResponse = await fetch("https://172.26.192.48:8443/change-number-of-plants/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plantId: selectedPlant.id, numberOfPlants: selectedNumberOfPlants }),
            }
        );

        const numberOfPlantsResult = await numberOfPlantsResponse.json();
        if (numberOfPlantsResult.status === "Success") {
            alert("Successfully changed number of plants!");
            setNumberOfPlants(selectedNumberOfPlants);
            navigate('/');
            return;
        } else if (numberOfPlantsResult.status === "Error") {
            alert("Failed to change number of plants.");
            navigate('/');
            return;
        }
    }

    const updateCurrPlant = async (e) => {
        e.preventDefault();

        const updateCurrPlantResponse = await fetch("https://172.26.192.48:8443/update-current-plant/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plantId: selectedCurrPlantId }),
            }
        );

        const updateCurrPlantResult = await updateCurrPlantResponse.json();
        if (updateCurrPlantResult.status === "Success") {
            alert("Successfully updated current plant!");
            fetchCurrentPlant();
            navigate('/');
            return;
        } else if (updateCurrPlantResult.status === "Error") {
            alert("Failed to update current plant.");
            navigate('/');
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
                <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
                    <Card className="mb-4">
                        <Card.Body>
                            <h3>Current Plant in Greenhouse: {currPlantName}</h3>
                            <p><strong>Health Status:</strong> {plantHealth || selectedPlant.health_status}</p>
                            <p><strong>Last Detected:</strong> {lastDetected}</p>
                            <Button variant="success" onClick={() => {
                                sendCommand({command: "get_plant_health_check"});
                                console.log("Get recent health status command sent!!!");
                                listenForHealthCheck();
                            }}>Get Recent Health Status of {currPlantName}</Button>

                            <div className="d-flex justify-content-center mb-4">
                                <Form onSubmit={updateCurrPlant}>
                                    <Form.Group className="mb-3">
                                    <Form.Label>Change Current Plant?</Form.Label>
                                        <Form.Select onChange={(e) => setSelectedCurrPlantId(e.target.value)} required>
                                            {plants.map((plant) => (
                                                <option key={plant.id} value={plant.id}>
                                                    {plant.name}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                    <Button variant="warning" type="submit">
                                        Submit
                                    </Button>
                                </Form>
                            </div>

                            <div className="d-flex justify-content-center mb-4">
                                <p><strong>Current Number of Plants:</strong> {numberOfPlants}</p>
                                <Form onSubmit={submitNumberOfPlants}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Change Number of Plants?</Form.Label>
                                        <Form.Select onChange={(e) => setSelectedNumberOfPlants(e.target.value)} required>
                                            <option value="1">1</option>
                                            <option value="2">2</option>
                                            <option value="3">3</option>
                                        </Form.Select>
                                    </Form.Group>
                                    <Button variant="warning" type="submit">
                                        Submit
                                    </Button>
                                </Form>
                            </div>

                            <div className="d-flex justify-content-center mb-3">
                                <Form.Check 
                                type="switch"
                                id="custom-switch"
                                label="Automatic Control Mode"
                                checked={automaticMode}
                                onChange={(e) => {
                                    const automaticState = e.target.checked;
                                    setAutomaticMode(automaticState);
                                    sendCommand({command: automaticState ? "automatic" : "manual"});
                                    automaticOrManual({command: automaticState, plantId: selectedPlant.id});
                                }}
                            />
                            </div>
                        </Card.Body>
                    </Card>
                </div>

                <div className="d-flex flex-wrap gap-3 justify-content-center">
                    <Button variant="active" onClick={() => navigate('/monitoring')}>📷 Live Camera</Button>
                    <Button variant="active" onClick={() => navigate('/plant-info')}>👀 View Plant Details</Button>
                    <Button variant="active" onClick={() => navigate('/control-command')}>🔌 Actuators</Button>
                </div>
            </div>
        );
    }


    return (
        <div className="home-page">
          <h1 className="mb-4">Welcome to Sproutly!</h1>
          {renderView()}
        </div>
      );
};


export default HomePage;