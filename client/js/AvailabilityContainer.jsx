import React from 'react'
import AvailabilityTable from './AvailabilityTable'
import { clone } from 'lodash'

export default class AvailabilityContainer extends React.Component {
  constructor(props) {
    super(props)
    this.state = clone(props)
  }

  render() {
    return <AvailabilityTable availabilities={this.state.availabilities} />;
  }
}
