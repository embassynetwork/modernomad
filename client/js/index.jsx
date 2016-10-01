import React from 'react'
import ReactDOM from 'react-dom'
import CapacityContainer from './components/CapacityContainer'
import RoomBooking from './components/booking/RoomBooking'

var topLevelComponents = {
  CapacityContainer : CapacityContainer,
  RoomBooking : RoomBooking
}

window.renderReactComponent = function(id, componentName, props) {
  var component = topLevelComponents[componentName];
  ReactDOM.render(React.createElement(component, props || {}), document.getElementById(id));
}
