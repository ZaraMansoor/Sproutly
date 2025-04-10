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

    const [camera, setCamera] = React.useState(false);
    
    let navigate = useNavigate();

    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
            <Form>
                <Form.Check 
                    type="switch"
                    id="custom-switch"
                    label="Camera Swtich"
                    checked={camera}
                    onChange={(e) => {
                        const cameraState = e.target.checked;
                        setCamera(cameraState);
                        sendCameraCommand({command: cameraState ? "on" : "off", actuator: "live_stream"});
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
                            <img src={`https://${RPI_IP_ADDRESS}:8444/stream.mjpg`} 
                                alt="Live Camera" 
                                width="640" 
                                height="480"
                            />
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