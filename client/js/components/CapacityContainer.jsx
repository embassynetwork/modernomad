import React, {PropTypes} from 'react'
import CapacityManager from './CapacityManager'
import ErrorDisplay from './ErrorDisplay'
import _ from 'lodash'
import axios from 'axios'
import moment from 'moment'

axios.defaults.xsrfCookieName = "csrftoken"
axios.defaults.xsrfHeaderName = "X-CSRFToken"

export default class CapacityContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ...props,
      upcomingCapacities: this.sortedCapacities(props.upcomingCapacities),
      formLoading: false
    }
  }

  static propTypes = {
    resourceId: PropTypes.number.isRequired
  }

  addCapacity(values) {
    this.setState({formLoading: true})

    axios.post(`/api/capacities/`, {
        start_date: moment(values.start_date).format("Y-MM-DD"),
        quantity: values.quantity,
        resource: this.props.resourceId
      })
      .then((response) => {
        this.setState({formLoading: false, errors: null, warnings: response.data.warnings})
        if (response.data.data) {
          this.insertCapacity(response.data.data)
        }
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

  displayWarnings(errors) {
    this.setState({warnings: warnings})
  }

  triggerDelete(capacityId) {
    axios.delete(`/api/capacity/${capacityId}`)
      .then((response) => {
        this.deleteCapacity(response.data.data.deleted.capacities)
      })
      .catch((error) => {
        console.log("error occured in delete", error);
      });
  }

  sortedCapacities(capacities) {
    return _.sortBy(capacities, (capacity) => {
      return moment(capacity.start_date)
    })
  }

  insertCapacity(capacity) {
    const withoutExisting = _.reject(this.state.upcomingCapacities, {id: capacity.id})
    const newCollection = this.sortedCapacities([...withoutExisting, capacity])
    this.setState({
      upcomingCapacities: newCollection
    })
  }

  deleteCapacity(deleted_capacities) {
    this.setState({
        upcomingCapacities: _.reject(this.state.upcomingCapacities, (capacity) => {
          return _.includes(deleted_capacities, capacity.id)
        })
    })
  }

  render() {
    return (
      <div>
        <CapacityManager
          currentCapacity={this.state.currentCapacity}
          upcomingCapacities={this.state.upcomingCapacities}
          formLoading={this.state.formLoading}
          onSubmitNew={this.addCapacity.bind(this)}
          onDelete={this.triggerDelete.bind(this)} />
        {this.state.errors && <ErrorDisplay errors={this.state.errors} category="danger" />}
        {this.state.warnings && <ErrorDisplay errors={this.state.warnings} category="warning" />}
      </div>
    )
  }
}
