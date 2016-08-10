import React, {PropTypes} from 'react'
import AvailabilityManager from './AvailabilityManager'
import { clone } from 'lodash'
import axios from 'axios'
import moment from 'moment'

axios.defaults.xsrfCookieName = "csrftoken"
axios.defaults.xsrfHeaderName = "X-CSRFToken"

export default class AvailabilityContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ...props,
      formLoading: false
    }
  }

  static propTypes = {
    resourceId: PropTypes.number.isRequired
  }

  addAvailability(values) {
    axios.post(`/api/resource/${this.props.resourceId}/availabilities/`, {
        start_date: moment(values.start_date).format(),
        quantity: values.quantity,
        resource: this.props.resourceId
      })
      .then((response) => {
        this.insertAvailability(response.data)
      })
      .catch((error) => {
        console.log("error occured", error);
      });
    //
    // // this.setState({formLoading: true})
    // console.log("values received from form", values)
  }

  insertAvailability(availability) {
    this.setState({
      upcomingAvailabilities: [...this.state.upcomingAvailabilities, availability]
    })
  }

  triggerDelete(availabilityId) {
    console.log('trigger delete', availabilityId)
  }

  render() {
    return <AvailabilityManager
      currentAvailability={this.state.currentAvailability}
      upcomingAvailabilities={this.state.upcomingAvailabilities}
      formLoading={this.state.formLoading}
      onSubmitNew={this.addAvailability.bind(this)}
      onDelete={this.triggerDelete.bind(this)} />;
  }
}
