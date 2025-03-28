import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Button, Form, Tab, Tabs } from 'react-bootstrap';

const ControlCommandPage = () => {

    const [plants, setPlants] = React.useState([]);
            
        React.useEffect(() => {
            fetch("http://localhost:8000/get-user-plants/")
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
        

    let navigate = useNavigate();

    const [waterPump, setWaterPump] = React.useState(false);
    const [mister, setMister] = React.useState(false);
    const [lights, setLights] = React.useState(false);
    const [heater, setHeater] = React.useState(false);
    const [nutrientDispenser, setNutrientDispenser] = React.useState(false);

    // TODO: add updating actuator on/off state from rpi logic later

    const sendCommand = async (commandData) => {
        try {
            const response = await fetch("http://localhost:8000/send-command/",
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

    // TODO: add on/off command logic later
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
            <Form>
                <Form.Check 
                    type="switch"
                    id="custom-switch"
                    label="Water Pump"
                    checked={waterPump}
                    onChange={(e) => {
                        sendCommand({command: "on", actuator: "water_pump"});
                    }}
                    
                />
                <Form.Check 
                    type="switch"
                    id="custom-switch"
                    label="Mister"
                    checked={mister}
                    onChange={(e) => {
                        sendCommand({command: "on", actuator: "mister"});
                    }}
                />
                <Form.Check 
                    type="switch"
                    id="custom-switch"
                    label="Lights"
                    checked={lights}
                    onChange={(e) => {
                        sendCommand({command: "on", actuator: "lights"});
                    }}
                />
                <Form.Check 
                    type="switch"
                    id="custom-switch"
                    label="Heater"
                    checked={heater}
                    onChange={(e) => {
                        sendCommand({command: "on", actuator: "heater"});
                    }}
                />
                <Form.Check 
                    type="switch"
                    id="custom-switch"
                    label="Nutrient Dispenser"
                    checked={nutrientDispenser}
                    onChange={(e) => {
                        sendCommand({command: "on", actuator: "nutrient_dispenser"});
                    }}
                />
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


export default ControlCommandPage;