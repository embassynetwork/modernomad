import React from 'react'
import ReactDOM from 'react-dom'
import AvailabilityTable from './AvailabilityTable'

var topLevelComponents = {}
topLevelComponents.AvailabilityTable = AvailabilityTable;

window.renderReactComponent = function(id, componentName) {
  var component = topLevelComponents[componentName];
  ReactDOM.render(React.createElement(component, {}), document.getElementById(id));
}
