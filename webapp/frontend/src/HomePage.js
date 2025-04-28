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
import socket from './socket';
import { Form } from 'react-bootstrap';
import { Button } from 'react-bootstrap';
import { Card } from 'react-bootstrap';
import { Container, Nav, Navbar, Alert, Badge } from 'react-bootstrap';

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

const HomePage = () => {

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

    const [numberOfPlants, setNumberOfPlants] = React.useState(null);


    const [selectedNumberOfPlants, setSelectedNumberOfPlants] = React.useState(1);
    const [selectedCurrPlantId, setSelectedCurrPlantId] = React.useState(1);

    const [currPlantName, setCurrPlantName] = React.useState(null);
    const [currPlantId, setCurrPlantId] = React.useState(null);
    const [currPlantSpecies, setCurrPlantSpecies] = React.useState(null);
    const [currPlantImage, setCurrPlantImage] = React.useState(null);
    const [currPlantHealth, setCurrPlantHealth] = React.useState(null);
    const [currPlantLastDetected, setCurrPlantLastDetected] = React.useState(null);


    const fetchCurrentPlant = () => {
        fetch("https://172.26.192.48:8443/get-current-plant/")
            .then(result => result.json())
            .then(data => {
                setCurrPlantName(data.current_plant_name);
                setCurrPlantId(data.current_plant_id);
                setCurrPlantSpecies(data.current_plant_species);
                setCurrPlantImage(data.current_plant_image);
                setCurrPlantHealth(data.current_plant_health_status);
                setCurrPlantLastDetected(data.current_plant_last_detected);
            })
            .catch(e => console.error("Failed to fetch current plant", e));
    };

    React.useEffect(() => {
        fetchCurrentPlant();
    }, []);


    React.useEffect(() => {
        if (!currPlantId) {
            return;
        }

        fetch("https://172.26.192.48:8443/get-number-of-plants/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ plantId: currPlantId })
        })
        .then(result => result.json())
        .then(data => {
            setNumberOfPlants(data.number_of_plants);
        }) 
        .catch(e => console.error("Failed to fetch number of plants", e));
    }, [currPlantId]);

    const [plantHealth, setPlantHealth] = React.useState(null);

    const [lastDetected, setLastDetected] = React.useState(null);

    const listenForHealthCheck = () => {
        const handler = (event) => {
            const data = JSON.parse(event.data);
            console.log("data.type:", data.type);

            if (data.type === "plant_health") {
                if (data.status === "Healthy") {
                    new Notification("Plant Health Alert!", {
                        body: `Plant ${currPlantName} is healthy! yay :)`
                    });
                    setPlantHealth("Healthy");
                    setLastDetected(data.time);
                }
                if (data.status === "Unhealthy") {
                new Notification("Plant Health Alert!", {
                        body: `Plant ${currPlantName} is unhealthy!`
                    });
                    setPlantHealth("Unhealthy");
                    setLastDetected(data.time);
                }
                socket.onmessage = null;
            }
        };
        socket.onmessage = handler;
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

        // if (!numberOfPlants) {
        //     alert("error with number of plants");
        //     return;
        // }

        const numberOfPlantsResponse = await fetch("https://172.26.192.48:8443/change-number-of-plants/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plantId: currPlantId, numberOfPlants: selectedNumberOfPlants }),
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
        return (
            <div>
                <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
                    <Card className="mb-4">
                        <Card.Header className="bg-secondary text-black">
                                <h5 className="mb-0">Current Plant</h5>
                        </Card.Header>
                        <Card.Body className="text-center">
                            <div className="text-center mt-4">
                                <img src={currPlantImage} alt="Plant" width="200" height="200" />
                            </div>
                            <h3>{currPlantName}</h3>
                            <p className="text-muted mb-3">
                                <i className="bi bi-tags me-2">
                                    {currPlantSpecies}
                                </i>
                            </p>

                            <div className="d-flex justify-content-center mb-3">
                                <Badge 
                                    bg={
                                        (plantHealth || currPlantHealth) === "Healthy" 
                                            ? "success" 
                                            : "warning"
                                    }
                                    className="d-flex align-items-center px-3 py-2"
                                >
                                    <div className="me-2 rounded-circle bg-white" 
                                            style={{
                                                width: "10px", 
                                                height: "10px",
                                                opacity: "0.7"
                                            }}
                                    />
                                    {plantHealth || currPlantHealth || 'Unknown'}
                                </Badge>
                            </div>
                            <p className="small text-muted mb-4">
                                <i className="bi bi-clock-history me-1"></i>
                                Last checked: {lastDetected || currPlantLastDetected}
                            </p>

                            <Button variant="success" onClick={() => {
                                listenForHealthCheck();
                                sendCommand({command: "get_plant_health_check"});
                                console.log("Get recent health status command sent!!!");
                            }} className="mb-4 w-100">
                                <i className="bi bi-heart-pulse me-2"></i>
                                Check Health Status
                            </Button>

                            <div className="d-flex justify-content-center mb-4">
                                <Form onSubmit={updateCurrPlant}>
                                    <Form.Group className="mb-3">
                                    <Form.Label>Change Current Plant</Form.Label>
                                        <Form.Select onChange={(e) => setSelectedCurrPlantId(e.target.value)} required>
                                            {plants.map((plant) => (
                                                <option key={plant.id} value={plant.id}>
                                                    {plant.name}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                    <Button variant="primary" type="submit" size="sm" className="w-100">
                                        <i className="bi bi-check-circle me-2"></i>
                                        Update
                                    </Button>
                                </Form>
                            </div>
                        </Card.Body>
                    </Card>
                </div>

                <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
                    <Card className="shadow-sm h-100">
                        <Card.Header className="bg-secondary text-black">
                            <h5 className="mb-0">Plant Controls</h5>
                        </Card.Header>
                        <Card.Body>
                            <Alert variant="info" className="d-flex align-items-center mb-4">
                                <i className="bi bi-info-circle-fill fs-4 me-3"></i>
                                <div>
                                    <strong>Plant Mode:</strong> Currently in {automaticMode ? "Automatic" : "Manual"} mode.
                                    {automaticMode
                                        ? ' Your plant is being automatically cared based on the auto-schedule.'
                                        : ' You can manually control your plant by turning on/off the Actuators. '}
                                </div>
                            </Alert>
                            <div className="d-flex justify-content-center mb-4">
                                <Form.Check 
                                type="switch"
                                id="custom-switch"
                                label="Automatic Control Mode"
                                checked={automaticMode}
                                onChange={(e) => {
                                    const automaticState = e.target.checked;
                                    setAutomaticMode(automaticState);
                                    sendCommand({command: automaticState ? "automatic" : "manual"});
                                    automaticOrManual({command: automaticState, plantId: currPlantId});
                                }}
                                className="fs-5"
                            />
                            </div>
                            
                            {automaticMode && (
                                <div className="d-flex flex-wrap gap-3 justify-content-center">
                                <Button variant="active" onClick={() => {
                                        navigate('/manual-autoschedule', {
                                            state: {
                                                plantId: currPlantId,
                                                numberOfPlants: numberOfPlants,
                                                plantSpecies: currPlantSpecies
                                            }
                                        })
                                        console.log("Setup auto control clicked!! plantId and numberOfPlants: ", currPlantId, numberOfPlants);
                                    }}>⏱️ Set Up Auto-schedule</Button>
                                </div>
                            )}

                            <div className="d-flex justify-content-center mb-4">
                                <Form onSubmit={submitNumberOfPlants}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Number of Plants in Greenhouse</Form.Label>
                                        <Form.Select onChange={(e) => setSelectedNumberOfPlants(e.target.value)} required className="me-2">
                                            <option value="1">1</option>
                                            <option value="2">2</option>
                                            <option value="3">3</option>
                                        </Form.Select>
                                    </Form.Group>
                                    <Button variant="outline-primary" type="submit">
                                        Update
                                    </Button>
                                    <Form.Text className="text-muted">
                                        Current Setting: {numberOfPlants} plant(s)
                                    </Form.Text>
                                </Form>
                            </div>

                            
                        </Card.Body>
                    </Card>
            </div>
            </div>
        );
    }


    return (
        <div className="home-page">
          <Header />
          <h1 className="mb-4">Welcome to Sproutly!</h1>
          {renderView()}
        </div>
      );
};


export default HomePage;