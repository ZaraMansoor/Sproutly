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

const MonitoringPage = () => {

    const [plants, setPlants] = React.useState([]);
        
    React.useEffect(() => {
        fetch("http://172.26.192.48:8000/get-user-plants/")
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

    const RPI_IP_ADDRESS = "172.26.192.48";
    
    let navigate = useNavigate();

    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
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
                            <img src={`http://${RPI_IP_ADDRESS}:8000/stream.mjpg`} 
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