import React from 'react'
import AvailabilityManager from './AvailabilityManager'
import { clone } from 'lodash'

export default class AvailabilityContainer extends React.Component {
  constructor(props) {
    super(props)
    this.state = clone(props)
  }

  render() {
    return <AvailabilityManager currentAvailability={this.state.currentAvailability} upcomingAvailabilities={this.state.upcomingAvailabilities} />;
  }
}
