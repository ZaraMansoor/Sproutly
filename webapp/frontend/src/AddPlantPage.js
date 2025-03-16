import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Form } from 'react-bootstrap';

const AddPlantPage = () => {

    // TODO: add actual plant data later
    const [plants, setPlants] = React.useState([
        { id: 1, name: 'Basil', species: 'Basil', health_status: 'Healthy' },
        { id: 2, name: 'Toma', species: 'Tomato', health_status: 'Unhealthy' },
    ]);

    const [plantName, setPlantName] = React.useState('');
    const [plantSpecies, setPlantSpecies] = React.useState('');

    // TODO: add add plant logic later

    let navigate = useNavigate();

    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
            
            <Form>
                <Form.Group className="mb-3">
                    <Form.Label>Plant Name</Form.Label>
                    <Form.Control type="text" placeholder="Enter plant name" 
                                onChange={(e) => setPlantName(e.target.value)}
                                required />
                </Form.Group>
                <Form.Group className="mb-3">
                    {/* TODO: add actual species data later, make it dropdown */}
                    <Form.Label>Species</Form.Label>
                    <Form.Control type="text" placeholder="Enter species" 
                                onChange={(e) => setPlantSpecies(e.target.value)}
                                required />
                </Form.Group>
                <Button variant="primary" type="submit">
                    Add Plant
                </Button>
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


export default AddPlantPage;