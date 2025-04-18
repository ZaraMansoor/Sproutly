import React from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';
import { Button, Form } from 'react-bootstrap';

const AddPlantPage = () => {

    const [plantName, setPlantName] = React.useState('');
    const [plantSpecies, setPlantSpecies] = React.useState('');
    const [numberOfPlants, setNumberOfPlants] = React.useState(null);

    let navigate = useNavigate();

    const [webscrapedPlantData, setWebscrapedPlantData] = React.useState([]);


    React.useEffect(() => {
        fetch("https://172.26.192.48:8443/plant-species/")
          .then(result => result.json())
          .then(data => {
            console.log("Species fetched!!:", data);
            setWebscrapedPlantData(data);
          })
          .catch(e => console.error("Failed to fetch plant species", e));
      }, []);
      
    
    const submitAddPlant = async (e) => {
        e.preventDefault();

        if (!plantName) {
            alert("error with plant name");
            return;
        }

        let selectedPlant = null;
        if (plantSpecies !== "no-species") {
            selectedPlant = webscrapedPlantData.find((plant) => plant.name === plantSpecies);
        }
        

        const userPlantResponse = await fetch("https://172.26.192.48:8443/add-user-plant/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: plantName, species: plantSpecies, numberOfPlants: numberOfPlants }),
            }
        );

        const userPlantResult = await userPlantResponse.json();
        if (userPlantResult.status === "detected plant not found") {
            navigate('/manual-autoschedule', {
                state: {
                    plantId: userPlantResult.plantId,
                    numberOfPlants: numberOfPlants
                }
            });
            return;
        }
        if (userPlantResult.status === "Error") {
            alert("Failed to add your new plant.");
            return;
        }

        const plantIndex = selectedPlant.index;

        const scrapeResponse = await fetch("https://172.26.192.48:8443/scrape-plant/",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ index: plantIndex, plantName: plantName, numberOfPlants: numberOfPlants }),
            }
        );

        const scrapeResult = await scrapeResponse.json();
        if (scrapeResult.status === "Success") {
            alert("Successfully added your new plant!");
            navigate('/');
        } else if (scrapeResult.status === "Error") {
            alert("Failed to add your new plant.");
        }
    };


    return (
        <div className="monitoring-page container d-flex flex-column vh-100">
          <div className="flex-grow-1 d-flex flex-column justify-content-center align-items-center text-center">
            
            <Form onSubmit={submitAddPlant}>
                <Form.Group className="mb-3">
                    <Form.Label>Plant Name</Form.Label>
                    <Form.Control type="text" placeholder="Enter plant name" 
                                onChange={(e) => setPlantName(e.target.value)}
                                required />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Species</Form.Label>
                    <Form.Select onChange={(e) => setPlantSpecies(e.target.value)} required>
                        <option value="">Select plant species</option>
                        <option key="-1" value="no-species">
                                I don't know my plant's species
                        </option>
                        {webscrapedPlantData.map((species) => (
                            <option key={species.index} value={species.name}>
                                {species.name}
                            </option>
                        ))}
                    </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Number of plants in your greenhouse</Form.Label>
                    <Form.Select onChange={(e) => setNumberOfPlants(e.target.value)} required>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </Form.Select>
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