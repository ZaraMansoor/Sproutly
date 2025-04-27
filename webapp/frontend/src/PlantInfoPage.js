
import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/brite/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Tab, Tabs } from 'react-bootstrap';
import socket from './socket';
import { Line } from 'react-chartjs-2';
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

const PlantInfoPage = () => {

    const [numberOfPlants, setNumberOfPlants] = React.useState(null);

    const [selectedPlant, setSelectedPlant] = React.useState(null);  // default

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
                    text: `${label} for the Last 24 Hours`, 
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
                window.location.reload();
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
                <h2>{selectedPlant.name}</h2>
                <p>Species: {selectedPlant.species}</p>

                <div className="d-flex flex-wrap gap-3 justify-content-center">
                    <Button variant="active" onClick={() => navigate('/add-plant')}>➕ Add New Plant</Button>
                    <Button variant="active" onClick={() => {
                        navigate('/manual-autoschedule', {
                            state: {
                                plantId: selectedPlant.id,
                                numberOfPlants: numberOfPlants
                            }
                        })
                        console.log("Setup auto control clicked!! plantId and numberOfPlants: ", selectedPlant.id, numberOfPlants);
                    }}>⏱️ Set Auto-schedule</Button>
                    <Button variant="danger" onClick={deletePlant}>🗑️ Delete Plant</Button>
                </div>
                
                <div className="text-center mt-4">
                    <img src={selectedPlant.image_url} alt="Plant" width="200" height="200" />
                </div>

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
          <h1 className="mb-4">Sproutly Dashboard</h1>
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


export default PlantInfoPage;