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
        <div className="monitoring-page container d-flex flex-column vh-100">
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
            <h3>Your plant has been detected as <b>{bestMatch}</b>. Common names are: {commonNames.join(", ")}. However, you'll need to manually set up an autoschedule for your plant.</h3>
            
            <div className="d-flex justify-content-center mb-4">
                <Button onClick={() => navigate('/manual-autoschedule', { 
                    state: {
                        plantId: location.state.plantId, numberOfPlants: location.state.numberOfPlants 
                    } 
                })}>
                    <i className="bi bi-arrow-left"></i>
                    Proceed to Manual Autoschedule
                </Button>
            </div>

          </div>
        </div>
      );
};


export default DetectionResultPage;