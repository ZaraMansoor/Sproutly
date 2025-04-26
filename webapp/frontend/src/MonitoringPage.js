/**
 * References:
 * https://react-bootstrap.netlify.app/docs/components/cards
 * https://react-bootstrap.netlify.app/docs/components/tabs
 * https://react-bootstrap.netlify.app/docs/components/buttons
 */

import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Card, Tab, Tabs, Button } from 'react-bootstrap';
import { Form } from 'react-bootstrap';

const MonitoringPage = () => {

    const [plants, setPlants] = React.useState([]);
        
    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-user-plants/")
            .then(result => result.json())
            .then(data => {
                setPlants(data);
            })
            .catch(e => console.error("Failed to fetch user plants", e));
    }, []);

    const [selectedPlant, setSelectedPlant] = React.useState(null);  // default

    React.useEffect(() => {
        if (!selectedPlant) {
            setSelectedPlant(plants[0]);
        }
    }, [plants]);

    const selectPlant = (plant) => {
        setSelectedPlant(plant);
    }


    const sendCameraCommand = async (cameraCommandData) => {
        try {
            const response = await fetch("https://172.26.192.48:8443/send-command/",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(cameraCommandData),
                });
            console.log("Camera control command sent", await response.json());
        } catch (error) {
            console.error("Error sending camera control command:", error);
        }
    }


    const RPI_IP_ADDRESS = "172.26.192.48";

    const [camera, setCamera] = React.useState(true);
    const [lights, setLights] = React.useState(false);


    const websocketRef = React.useRef(null);

    React.useEffect(() => {
        const websocket = new WebSocket('wss://172.26.192.48:8443/ws/sproutly/actuator/');
        websocketRef.current = websocket;

        let live_stream_status = "null";
        let white_light_status = "null";    
        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Received data from websocket:", data);
            live_stream_status = data["live_stream"];
            white_light_status = data["white_light"];
            if (live_stream_status === "on") {
                setCamera(true);
            } else if (live_stream_status === "off") {
                setCamera(false);
            }
            if (white_light_status === "on") {
                setLights(true);
            } else if (white_light_status === "off") {
                setLights(false);
            }
        }

        return () => {
            websocket.close(); 
        };
    }, []);
    
    
    React.useEffect(() => {
        const getInitialActuatorStatus = async () => {
            try {
                const response = await fetch("https://172.26.192.48:8443/send-command/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ command: "get_actuators_status" }),
            });
            const data = await response.json();
            console.log("Initial actuator status:", data);
            }  catch (error) {
                console.error("Error getting initial actuator status:", error);
            }
        };

        getInitialActuatorStatus();
    }, []);

    ////
    
    let navigate = useNavigate();

    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
            <Form>
                <Form.Check 
                    type="switch"
                    id="custom-switch"
                    label="Camera Switch"
                    checked={camera}
                    onChange={(e) => {
                        const cameraState = e.target.checked;
                        setCamera(cameraState);
                        sendCameraCommand({command: cameraState ? "on" : "off", actuator: "live_stream"});
                    }}
                />
                <Form.Check
                    type="switch"
                    id="lights-switch"
                    label="Lights"
                    checked={lights}
                    onChange={(e) => {
                        const lightsState = e.target.checked;
                        setLights(lightsState);
                        sendCameraCommand({command: lightsState ? "on" : "off", actuator: "white_light"});
                    }}
                />
            </Form>
          </div>
          <div className="d-flex justify-content-between align-items-center mb-4">

            <Tabs activeKey={selectedPlant ? selectedPlant.id.toString() : null} onSelect={(key) => {
                const plant = plants.find(p => p.id.toString() === key);
                if (plant) selectPlant(plant);
            }} className="flex-grow-1">
            {plants.map((plant) => (
            <Tab
                key={plant.id}
                eventKey={plant.id.toString()}
                title={plant.name}
            />
            ))}
            </Tabs>
          </div>
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
                {selectedPlant && (
                <div className="d-flex align-items-center">
                    <Card className="shadow-sm">
                        <Card.Body>
                            <h2 className="mb-3">{selectedPlant.name} Live Feed</h2>
                            {camera ? (
                                <img
                                    src={`https://${RPI_IP_ADDRESS}:8444/stream.mjpg`}
                                    alt="Live Camera"
                                    width="640"
                                    height="480"
                                />
                            ) : (
                                <p>Camera is off</p>
                            )}
                        </Card.Body>
                    </Card>
                </div>)}

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


export default MonitoringPage;