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


    // notification permission handling
    Notification.requestPermission().then((result) => {
        console.log(result);
        if (result === "granted") {
            console.log("Notification permission granted");
        } else {
            console.log("Notification permission denied");
        }
    });


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
            console.log("Sensor data chart update attempting...");
            const data = JSON.parse(event.data);

            console.log("data.type:", data.type);
            if (data.type === "plant_health") {
                if (selectedPlant && selectedPlant.health_status === "healthy" &&
                    data.health_status === "unhealthy") {
                    new Notification("Plant Health Alert!", {
                        body: `Plant ${selectedPlant.name} is now unhealthy!`
                    });
                return;
                }
            }

            const timestampedData = {
                ...data,
                timestamp: new Date().toLocaleString(),
            };

            // send notifications
            if (plantInfo) {
                notifications = []
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
    


    

    const [selectedPlant, setSelectedPlant] = React.useState(null);  // default
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



    let navigate = useNavigate();

    const renderView = () => {
        if (!selectedPlant) {
            return (
                <div>
                    <h2>Loading...</h2>
                </div>
            )
        }
        if (currView === 'home') {
            return renderHomeView();
        } else if (currView === 'schedule') {
            return renderScheduleView();
        } // TODO: add different control views
    }

    const renderHomeView = () => {
        return (
            <div>
                <p>If you want to get notifications when your plant is unhealthy, click this to enable notifications on your browser.</p>
                <button onClick={() => Notification.requestPermission()}>Enable Notifications</button>
                <h2>{selectedPlant.name}</h2>
                <p>Health Status: {selectedPlant.health_status === 'healthy' ? 'Healthy' : 'Unhealthy'}</p>
                <p>Species: {selectedPlant.species}</p>

                {/* TODO: control buttons */}

                <button onClick={() => navigate('/monitoring')}>Live Camera</button>
                <button onClick={() => navigate('/add-plant')}>Add Plant</button>
                <button onClick={() => setCurrView('schedule')}>Set Up Auto Control</button>
                <button onClick={() => navigate('/control-command')}>Turn On/Off Actuators</button>
                
                <img src={selectedPlant.image_url} alt="Plant" width="200" height="200" />

                <SensorChart label="Temperature (°C)" dataKey="temperature_c" color="red" />
                <SensorChart label="Temperature (°F)" dataKey="temperature_f" color="blue" />
                <SensorChart label="Humidity (%)" dataKey="humidity" color="green" />

                <h2>Ideal Plant Care Conditions for {selectedPlant.name}</h2>
                <p>Scientific Name: {plantInfo.scientific_name}</p>
                <p>Light: {plantInfo.light_description}</p>
                <p>Light Start Time: {plantInfo.light_t0}</p>
                <p>Light Duration: {plantInfo.light_duration} hours</p>
                <p>Water: {plantInfo.water_description}</p>
                <p>Minimum Temperature: {plantInfo.temp_min} °F</p>
                <p>Maximum Temperature: {plantInfo.temp_max} °F</p>
                <p>Minimum Humidity: {plantInfo.humidity_min} %</p>
                <p>Maximum Humidity: {plantInfo.humidity_max} %</p>
            </div>
        );
    }

    const renderScheduleView = () => {
        return (
            <div>
                <h2>Auto-schedule Setup</h2>
                <p>Recommended: </p>
                <p>Water: </p>
                <p>Recommended: </p>
                <p>Moisture: </p>
                <p>Recommended: </p>
                <p>Temperature: </p>
                {/* TODO */}
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