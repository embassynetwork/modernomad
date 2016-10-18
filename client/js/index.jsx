import React from 'react'
import ReactDOM from 'react-dom'
import App from './components/App'
import CapacityContainer from './components/capacity/CapacityContainer'
import RoomBooking from './components/booking/RoomBooking'

var topLevelComponents = {
  CapacityContainer : CapacityContainer,
  RoomBooking : RoomBooking
}

window.renderReactComponent = function(id, componentName, props) {
  var component = topLevelComponents[componentName];
  var componentInstance = React.createElement(component, props || {})
  var appComponent = React.createElement(App, {}, componentInstance)
  ReactDOM.render(appComponent, document.getElementById(id));
}
