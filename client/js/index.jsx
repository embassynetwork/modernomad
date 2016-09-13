import React from 'react'
import ReactDOM from 'react-dom'
import AvailabilityContainer from './components/AvailabilityContainer'
import RoomBooking from './components/booking/RoomBooking'

var topLevelComponents = {
  AvailabilityContainer : AvailabilityContainer,
  RoomBooking : RoomBooking
}

window.renderReactComponent = function(id, componentName, props) {
  var component = topLevelComponents[componentName];
  ReactDOM.render(React.createElement(component, props || {}), document.getElementById(id));
}
