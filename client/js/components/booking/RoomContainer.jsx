import React, {PropTypes} from 'react'
import { browserHistory } from 'react-router'
import RoomIndex from './RoomIndex'
import _ from 'lodash'

function formatDate(date) {
  return date ? date.format('MM/DD/YYYY') : null
}

function formatDateRange(dates) {
  return {arrive: formatDate(dates.arrive), depart: formatDate(dates.depart)}
}

export default class RoomContainer extends React.Component {
  constructor(props) {
    super(props)
  }

  reFilter(filters) {
    browserHistory.push({
      pathname: '/locations/'+this.props.routeParams.location+'/stay/',
      query: formatDateRange(filters.dates)
    })
  }

  render() {
    return <RoomIndex
      rooms={this.props.rooms}
      routeParams={this.props.routeParams}
      query={this.props.location.query}
      networkLocation={this.props.networkLocation}
      onFilterChange={this.reFilter.bind(this)} />
  }
}
