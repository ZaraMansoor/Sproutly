import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/brite/bootstrap.min.css';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from 'react-bootstrap';

const DetectionResultPage = () => {
    
    let navigate = useNavigate();
    let location = useLocation();

    const [bestMatch, setBestMatch] = React.useState([]);
    const [commonNames, setCommonNames] = React.useState([]);
    
    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/get-detection-result/")
            .then(result => result.json())
            .then(data => {
                setBestMatch(data.best_match);
                setCommonNames(data.common_names);
                console.log("Detection result:", data);
            })
            .catch(e => console.error("Failed to fetch plant detection result", e));
    }, []);


    return (
        <div className="container d-flex flex-column justify-content-center align-items-center vh-100">
            <Card className="shadow-sm mb-4 w-100 max-w-md">
                <Card.Body className="text-center">
                    <Card.Title className="mb-4">Plant Detection Results</Card.Title>
                    
                    <Alert variant="success">
                        <p className="mb-0">
                            Your plant has been detected as <strong>{bestMatch}</strong>
                        </p>
                    </Alert>
                    
                    <div className="mt-4">
                        <h5>Common Names:</h5>
                        <p>{commonNames.join(", ")}</p>
                    </div>
                    
                    <div className="mt-4">
                        <p className="text-muted">
                            You'll need to set up an auto-schedule with the ideal growing conditions.
                        </p>
                    </div>
                </Card.Body>
                <Card.Footer className="bg-transparent border-0 text-center pb-4">
                    <Button 
                        variant="primary" 
                        size="lg"
                        onClick={() => navigate('/manual-autoschedule', { 
                            state: {
                                plantId: location.state?.plantId, 
                                numberOfPlants: location.state?.numberOfPlants 
                            } 
                        })}
                    >
                        Set Up Auto-Schedule
                    </Button>
                    
                    <div className="mt-2">
                        <Button variant="outline-secondary" onClick={() => navigate('/')}>
                            <i className="bi bi-arrow-left"></i> Return Home
                        </Button>
                    </div>
                </Card.Footer>
            </Card>
        </div>
      );
};


export default DetectionResultPage;