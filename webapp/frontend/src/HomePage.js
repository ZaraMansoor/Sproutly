import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Tab, Tabs } from 'react-bootstrap';
import socket from './socket';

const HomePage = () => {

    const [plants, setPlants] = React.useState([]);
    
    React.useEffect(() => {
        fetch("http://localhost:8000/get-user-plants/")
            .then(result => result.json())
            .then(data => {
                setPlants(data);
            })
            .catch(e => console.error("Failed to fetch user plants", e));
    }, []);


    // TODO: add actual sensor data later
    // const sensorData = {
    //     temperature: 25,
    //     humidity: 50,
    //     light: 100,
    //     soil_moisture: 75,
    //     ph: 7.5,
    //     nutrients: 50
    // };

    const [sensorData, setSensorData] = React.useState({});

    React.useEffect(() => {
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setSensorData(data);
        };

        return () => socket.close();
    }, []);
    

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
                <h2>{selectedPlant.name}</h2>
                <p>Health Status: {selectedPlant.health_status === 'healthy' ? 'Healthy' : 'Unhealthy'}</p>
                <p>Species: {selectedPlant.species}</p>

                {/* TODO: control buttons */}

                <button onClick={() => navigate('/monitoring')}>Live Camera</button>
                <button onClick={() => navigate('/add-plant')}>Add Plant</button>
                <button onClick={() => setCurrView('schedule')}>Set Up Auto Control</button>
                <button onClick={() => navigate('/control-command')}>Turn On/Off Actuators</button>
                
                <p>Temperature: {sensorData.temperature}°C</p>
                <p>Humidity: {sensorData.humidity}%</p>
                <p>Light: {sensorData.light} lux</p>
                <p>Soil Moisture: {sensorData.soil_moisture}%</p>
                <p>pH: {sensorData.ph}</p>
                <p>Nutrients: {sensorData.nutrients}mL</p>
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