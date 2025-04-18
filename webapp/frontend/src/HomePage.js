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
import { useNavigate } from 'react-router-dom';
import { Tab, Tabs } from 'react-bootstrap';
import socket from './socket';
import { Line } from 'react-chartjs-2';
import { Form } from 'react-bootstrap';
import { Button } from 'react-bootstrap';

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

    const [selectedPlant, setSelectedPlant] = React.useState(null);  // default

    React.useEffect(() => {
        if (!selectedPlant) {
            return;
        }

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


    const [plantHealth, setPlantHealth] = React.useState([]);

    // display 24 hours long of sensor data (sensor data is sent every 1 min)
    const [sensorDataHistory, setSensorDataHistory] = React.useState([]);


    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-sensor-data-history/")
            .then(res => res.json())
            .then(data => {
                console.log("Fetching past sensor data history:", data);
                setSensorDataHistory(data);
            })
            .catch(e => console.error("Failed to fetch sensor data history", e));
    }, []);


    React.useEffect(() => {
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("data.type:", data.type);
            if (data.type === "plant_health") {
                if (selectedPlant && data.status === "Healthy") {
                    new Notification("Plant Health Alert!", {
                        body: `Plant ${selectedPlant.name} is healthy! yay :)`
                    });
                    setPlantHealth("Healthy");
                    return;
                }
                if (selectedPlant && data.status === "Unhealthy") {
                    new Notification("Plant Health Alert!", {
                        body: `Plant ${selectedPlant.name} is unhealthy!`
                    });
                    setPlantHealth("Unhealthy");
                    return;
                }
            }

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
                    text: `${label} for the Last 24 Hours`, 
                }
            }
        };
    
        return <Line data={data} options={options} />;
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
                body: JSON.stringify({ numberOfPlants: numberOfPlants }),
            }
        );

        const numberOfPlantsResult = await numberOfPlantsResponse.json();
        if (numberOfPlantsResult.status === "Success") {
            alert("Successfully changed number of plants!");
            navigate('/');
        } else if (numberOfPlantsResult.status === "Error") {
            alert("Failed to change number of plants.");
            navigate('/');
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
                {/* <p>If you want to get notifications when your plant is unhealthy, click this to enable notifications on your browser.</p>
                <button onClick={() => {
                    Notification.requestPermission().then((result) => {
                        console.log(result);
                        if (result === "granted") {
                            console.log("Notification permission granted");
                        } else {
                            console.log("Notification permission denied");
                        }
                    });
                }}>Enable Notifications</button> */}

                <h2>{selectedPlant.name}</h2>
                <p>Health Status: {plantHealth || selectedPlant.health_status}</p>
                <p>Species: {selectedPlant.species}</p>

                {/* TODO: control buttons */}

                <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
                    <Form>
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
                    </Form>
                </div>
                <p>Current Number of Plants: {numberOfPlants}</p>
                <Form onSubmit={submitNumberOfPlants}>
                    <Form.Label>Change Number of Plants</Form.Label>
                    <Form.Select onChange={(e) => setNumberOfPlants(e.target.value)} required>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </Form.Select>
                    <Button variant="primary" type="submit">
                        Submit
                    </Button>
                </Form>

                <button onClick={() => {
                    sendCommand({command: "get_plant_health_check"});
                    console.log("Get recent health status command sent!!!");
                }}>Get Recent Health Status</button>
                <button onClick={() => navigate('/monitoring')}>Live Camera</button>
                <button onClick={() => navigate('/add-plant')}>Add Plant</button>
                <button onClick={() => navigate('/manual-autoschedule')}>Set Up Auto Control</button>
                <button onClick={() => navigate('/control-command')}>Turn On/Off Actuators</button>
                
                <img src={selectedPlant.image_url} alt="Plant" width="200" height="200" />

                <SensorChart label="Temperature (°C)" dataKey="temperature_c" color="red" />
                <SensorChart label="Temperature (°F)" dataKey="temperature_f" color="blue" />
                <SensorChart label="Humidity (%)" dataKey="humidity" color="green" />
                <SensorChart label="Soil Moisture (%)" dataKey="soil_moisture" color="purple" />
                <SensorChart label="Light (lux)" dataKey="lux" color="yellow" />
                <SensorChart label="pH" dataKey="ph" color="orange" />
                <SensorChart label="Soil Temperature (°C)" dataKey="soil_temp" color="pink" />
                <SensorChart label="Conductivity (uS/cm)" dataKey="conductivity" color="brown" />
                <SensorChart label="Nitrogen (mg/kg)" dataKey="nitrogen" color="teal" />
                <SensorChart label="Phosphorus (mg/kg)" dataKey="phosphorus" color="maroon" />
                <SensorChart label="Potassium (mg/kg)" dataKey="potassium" color="olive" />

                <h2>Ideal Plant Care Conditions for {selectedPlant.name}</h2>
                <p>Scientific Name: {plantInfo.scientific_name}</p>
                <p>Light: {plantInfo.light_description}</p>
                <p>Light Intensity: {plantInfo.light_intensity}</p>
                <p>Water: {plantInfo.water_description}</p>
                <p>Minimum Temperature: {plantInfo.temp_min} °F</p>
                <p>Maximum Temperature: {plantInfo.temp_max} °F</p>
                <p>Minimum Humidity: {plantInfo.humidity_min} %</p>
                <p>Maximum Humidity: {plantInfo.humidity_max} %</p>
                <p>Minimum pH: {plantInfo.ph_min}</p>
                <p>Maximum pH: {plantInfo.ph_max}</p>
            </div>
        );
    }


    return (
        <div className="home-page">
          <h1 className="mb-4">Sproutly</h1>
          <div className="d-flex justify-content-between align-items-center mb-3">
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
          {renderView()}
        </div>
      );
};


export default HomePage;