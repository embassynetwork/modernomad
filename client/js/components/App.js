import React from 'react';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

const App = (props) => (
  <MuiThemeProvider>
    {props.children}
  </MuiThemeProvider>
);

export default App
