import React from 'react'
import AvailabilityManager from './AvailabilityManager'
import { clone } from 'lodash'
import axios from 'axios'

export default class AvailabilityContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ...props,
      formLoading: false
    }
  }

  addAvailability(values) {
    // this.setState({
    //   upcomingAvailabilities: [...this.state.upcomingAvailabilities, values]
    // })

    axios.post(`/api/resource/141/availabilities`, {
        firstName: 'Fred',
        lastName: 'Flintstone'
      })
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });

    // this.setState({formLoading: true})
    console.log("values received from form", values)
  }

  render() {
    return <AvailabilityManager
      currentAvailability={this.state.currentAvailability}
      upcomingAvailabilities={this.state.upcomingAvailabilities}
      formLoading={this.state.formLoading}
      onSubmitNew={this.addAvailability.bind(this)} />;
  }
}
