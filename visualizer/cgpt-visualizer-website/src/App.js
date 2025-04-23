import React from 'react';
import GenomeBrowser from './GenomeBrowser';
import './App.css';

function App() {
  return (
    <div className="App" style={{height: '100vh', width: '100vw', margin: 0, padding: 0, overflow: 'hidden'}}>
      <GenomeBrowser />
    </div>
  );
}

export default App;
