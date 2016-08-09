import React from 'react'
import AvailabilityManager from './AvailabilityManager'
import { clone } from 'lodash'

export default class AvailabilityContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {...props}
  }

  addAvailability(values) {
    console.log("values received from form", values)
    alert("Now I need to talk to the endpoint. - Craig")
  }

  render() {
    return <AvailabilityManager
      currentAvailability={this.state.currentAvailability}
      upcomingAvailabilities={this.state.upcomingAvailabilities}
      onSubmitNew={this.addAvailability.bind(this)} />;
  }
}
