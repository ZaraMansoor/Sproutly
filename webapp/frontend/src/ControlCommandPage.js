/**
 * References for React and Bootstrap:
 * https://react.dev/reference/react
 * https://react-bootstrap.netlify.app/docs/forms/checks-radios/
 * https://dev.to/collegewap/how-to-work-with-checkboxes-in-react-44bc
 * https://mui.com/material-ui/react-slider/
 */

import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/brite/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Button, Form, Tab, Tabs } from 'react-bootstrap';
import { Slider } from '@mui/material';
import { Container, Nav, Navbar } from 'react-bootstrap';


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
  
const ControlCommandPage = () => {


    const [automaticState, setAutomaticState] = React.useState(null);


    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-automatic-or-manual/")
            .then(result => result.json())
            .then(data => {
                console.log("Automatic or Manual fetched!!:", data);
                setAutomaticState(data["automatic_or_manual"]);
            })
            .catch(e => console.error("Failed to fetch automatic or manual", e));
    }, [])


    const [waterPump, setWaterPump] = React.useState(false);
    const [mister, setMister] = React.useState(false);
    const [lights, setLights] = React.useState(false);
    const [heater, setHeater] = React.useState(false);
    const [nutrientsPump, setNutrientsPump] = React.useState(false);

    const [lightValue, setLightValue] = React.useState(0);


    // TODO: have to test

    const websocketRef = React.useRef(null);

    React.useEffect(() => {
        const websocket = new WebSocket('wss://172.26.192.48:8443/ws/sproutly/actuator/');
        websocketRef.current = websocket;

        let heater_status = "null";
        let water_pump_status = "null";
        let nutrients_pump_status = "null";
        let mister_status = "null";
        let white_light_status = "null";
        let LED_light_status = "null";

        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Received data from websocket:", data);
            heater_status = data["heater"];
            water_pump_status = data["water_pump"];
            nutrients_pump_status = data["nutrients_pump"];
            mister_status = data["mister"];
            white_light_status = data["white_light"];
            LED_light_status = data["LED_light"];
            
            if (heater_status === "on") {
                setHeater(true);
            } else if (heater_status === "off") {
                setHeater(false);
            }
            if (water_pump_status === "on") {
                setWaterPump(true);
            } else if (water_pump_status === "off") {
                setWaterPump(false);
            }
            if (nutrients_pump_status === "on") {
                setNutrientsPump(true);
            } else if (nutrients_pump_status === "off") {
                setNutrientsPump(false);
            }
            if (mister_status === "on") {
                setMister(true);
            } else if (mister_status === "off") {
                setMister(false);
            }
            if (white_light_status === "on") {
                setLights(true);
            } else if (white_light_status === "off") {
                setLights(false);
            }
            if (LED_light_status === 0) {
                setLightValue(0);
            } else if (LED_light_status === 1) {
                setLightValue(1);
            } else if (LED_light_status === 2) {
                setLightValue(2);
            } else if (LED_light_status === 3) {
                setLightValue(3);
            } else if (LED_light_status === 4) {
                setLightValue(4);
            }
        }

        return () => {
            websocket.close(); 
        };
    }, []);
    
    
    ///////

    let navigate = useNavigate();

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

    // TODO: have to test
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

    if (automaticState === null) {
        return (
            <p>Loading...</p>
        )
    }

    console.log("automaticState???????:", automaticState, typeof automaticState);
    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
            <Header />
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
            <div className="d-flex justify-content-center mb-4">
                <Form disabled = {automaticState === true}>
                    <Form.Check
                        type="switch"
                        id="water-switch"
                        label="Water Pump"
                        checked={waterPump}
                        onChange={(e) => {
                            const waterPumpState = e.target.checked;
                            setWaterPump(waterPumpState);
                            sendCommand({command: waterPumpState ? "on" : "off", actuator: "water_pump"});
                        }}
                        disabled = {automaticState === true}
                    />
                    <Form.Check
                        type="switch"
                        id="mister-switch"
                        label="Mister"
                        checked={mister}
                        onChange={(e) => {
                            const misterState = e.target.checked;
                            setMister(misterState);
                            sendCommand({command: misterState ? "on" : "off", actuator: "mister"});
                        }}
                        disabled = {automaticState === true}
                    />
                    <Form.Check
                        type="switch"
                        id="lights-switch"
                        label="Lights"
                        checked={lights}
                        onChange={(e) => {
                            const lightsState = e.target.checked;
                            setLights(lightsState);
                            sendCommand({command: lightsState ? "on" : "off", actuator: "white_light"});
                        }}
                        disabled = {automaticState === true}
                    />
                    <div className="my-4">
                        <p>LED Brightness: {lightValue}</p>
                        <Slider
                            min={0}
                            max={4}
                            step={1}
                            value={lightValue}
                            onChange={(e) => {
                                const newLightValue = e.target.value;
                                setLightValue(newLightValue);
                                sendCommand({ command: newLightValue, actuator: "LED_light" }); 
                            }}
                            disabled = {automaticState === true}
                        />
                    </div>
                    <Form.Check
                        type="switch"
                        id="heater-switch"
                        label="Heater"
                        checked={heater}
                        onChange={(e) => {
                            const heaterState = e.target.checked;
                            setHeater(heaterState);
                            sendCommand({command: heaterState ? "on" : "off", actuator: "heater"});
                        }}
                        disabled = {automaticState === true}
                    />
                    <Form.Check
                        type="switch"
                        id="nutrients-switch"
                        label="Nutrients Pump"
                        checked={nutrientsPump}
                        onChange={(e) => {
                            const nutrientsPumpState = e.target.checked;
                            setNutrientsPump(nutrientsPumpState);
                            sendCommand({command: nutrientsPumpState ? "on" : "off", actuator: "nutrients_pump"});
                        }}
                        disabled = {automaticState === true}
                    />
                </Form>
            </div>

          </div>
        </div>
      );
};


export default ControlCommandPage;