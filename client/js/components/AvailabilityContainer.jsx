import React, {PropTypes} from 'react'
import AvailabilityManager from './AvailabilityManager'
import ErrorDisplay from './ErrorDisplay'
import { clone, reject, sortBy } from 'lodash'
import axios from 'axios'
import moment from 'moment'

axios.defaults.xsrfCookieName = "csrftoken"
axios.defaults.xsrfHeaderName = "X-CSRFToken"

export default class AvailabilityContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ...props,
      upcomingAvailabilities: this.sortedAvailabilities(props.upcomingAvailabilities),
      formLoading: false
    }
  }

  static propTypes = {
    resourceId: PropTypes.number.isRequired
  }

  addAvailability(values) {
    this.setState({formLoading: true})

    axios.post(`/api/availabilities/`, {
        start_date: moment(values.start_date).format("Y-MM-DD"),
        quantity: values.quantity,
        resource: this.props.resourceId
      })
      .then((response) => {
        this.setState({formLoading: false, errors: null})
        this.insertAvailability(response.data)
      })
      .catch((error) => {
        this.setState({formLoading: false})
        if (error.response.status == '400' && error.response.data.errors) {
          this.displayErrors(error.response.data.errors);
        } else {
          console.log("error occured in post", error);
        }
      });
  }

  displayErrors(errors) {
    this.setState({errors: errors})
  }

  triggerDelete(availabilityId) {
    axios.delete(`/api/availability/${availabilityId}`)
      .then((response) => {
        this.deleteAvailability(availabilityId)
      })
      .catch((error) => {
        console.log("error occured in delete", error);
      });
  }

  sortedAvailabilities(availabilities) {
    return sortBy(availabilities, (availability) => {
      return moment(availability.start_date)
    })
  }

  insertAvailability(availability) {
    const newCollection = this.sortedAvailabilities([...this.state.upcomingAvailabilities, availability])
    this.setState({
      upcomingAvailabilities: newCollection
    })
  }

  deleteAvailability(availabilityId) {
    this.setState({
      upcomingAvailabilities: reject(this.state.upcomingAvailabilities, {id: availabilityId})
    })
  }

  render() {
    return (
      <div>
        <AvailabilityManager
          currentAvailability={this.state.currentAvailability}
          upcomingAvailabilities={this.state.upcomingAvailabilities}
          formLoading={this.state.formLoading}
          onSubmitNew={this.addAvailability.bind(this)}
          onDelete={this.triggerDelete.bind(this)} />
        {this.state.errors && <ErrorDisplay errors={this.state.errors} />}
      </div>
    )
  }
}
