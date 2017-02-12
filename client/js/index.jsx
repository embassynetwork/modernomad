import React from 'react'
import ReactDOM from 'react-dom'
import App from './components/App'
import CapacityContainer from './components/capacity/CapacityContainer'
import RoomBooking from './components/booking/RoomBooking'
import Backings from './components/backing/Backings'
import CurrentBacking from './components/backing/CurrentBacking'

var topLevelComponents = {
  CapacityContainer : CapacityContainer,
  RoomBooking : RoomBooking,
  Backings: Backings, 
  CurrentBacking: CurrentBacking
}

window.renderReactComponent = function(id, componentName, props) {
  var component = topLevelComponents[componentName];
  var componentInstance = React.createElement(component, props || {})
  var appComponent = React.createElement(App, {}, componentInstance)
  ReactDOM.render(appComponent, document.getElementById(id));
}
