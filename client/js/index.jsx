import React from 'react'
import ReactDOM from 'react-dom'
import AvailabilityContainer from './components/AvailabilityContainer'

var topLevelComponents = {}
topLevelComponents.AvailabilityContainer = AvailabilityContainer;

window.renderReactComponent = function(id, componentName, props) {
  var component = topLevelComponents[componentName];
  ReactDOM.render(React.createElement(component, props), document.getElementById(id));
}
