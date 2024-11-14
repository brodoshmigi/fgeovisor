// App.js
import React, { useEffect, useState, useRef } from 'react';

const App = () => {
    return (
      <div>
        <h1>Welcome to my React App</h1>
        <img src="/static/images/logo.png" alt="Logo" />
        <div className="background" style={{ backgroundImage: 'url(/static/images/background.jpg)' }}>
          This is a background image.
        </div>
      </div>
    );
  };
  
  export default App;