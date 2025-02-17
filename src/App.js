import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

// Import des pages (composants) pour chaque route
import LayoutHome from './components/LayoutHome';
import LayoutLogement from './components/LayoutLogement';
import LayoutSante from './components/LayoutSante';
import LayoutPredictions from './components/LayoutPredictions';
import LayoutTransports from './components/LayoutTransports';

function App() {
  return (
    <div className="App" style={{ backgroundColor: 'black', color: 'white' }}>
      <Router>
        <Switch>
          {/* Définition des routes et des composants associés */}
          <Route path="/" exact component={LayoutHome} />
          <Route path="/logement" component={LayoutLogement} />
          <Route path="/sante" component={LayoutSante} />
          <Route path="/predictions" component={LayoutPredictions} />
          <Route path="/transports" component={LayoutTransports} />
        </Switch>
      </Router>
    </div>
  );
}

export default App;
