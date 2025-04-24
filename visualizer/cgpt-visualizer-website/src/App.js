import React, { useEffect, useState } from 'react';
import GenomeBrowser, { realChromosome } from './GenomeBrowser';
import './App.css';

function App() {
  // Use React state for genes
  const [genes, setGenes] = useState([]);

  useEffect(() => {
    const apiUrl = `http://localhost:5001/api/v1/genes?chromosome=${realChromosome.name}`;
    console.log(`[App Effect] Fetching genes for ${realChromosome.name} from: ${apiUrl}`);

    fetch(apiUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data && Array.isArray(data)) {
          setGenes(data);
          console.log(`[App Effect] Successfully stored ${data.length} genes in the state.`);
        } else {
          console.error('[App Effect] Invalid data format received:', data);
          setGenes([]);
        }
      })
      .catch(error => {
        console.error('[App Effect] Error fetching or processing genes:', error);
        setGenes([]);
      });

  }, []);

  return (
    <div className="App" style={{ height: '100vh', width: '100vw', margin: 0, padding: 0, overflow: 'hidden' }}>
      <GenomeBrowser genes={genes} />
      {/* You can add other UI elements here if needed */}
      {/* Example: <p>Fetched genes are in state. Check console.</p> */}
    </div>
  );
}

export default App;
