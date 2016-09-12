import React from 'react'
import ReactDOM from 'react-dom'
import AvailabilityContainer from './components/AvailabilityContainer'
import RoomContainer from './components/booking/RoomContainer'

var topLevelComponents = {
  AvailabilityContainer : AvailabilityContainer,
  RoomContainer : RoomContainer
}

window.renderReactComponent = function(id, componentName, props) {
  var component = topLevelComponents[componentName];
  ReactDOM.render(React.createElement(component, props || {}), document.getElementById(id));
}
