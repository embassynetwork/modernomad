import React, {PropTypes} from 'react'
import { browserHistory } from 'react-router'
import RoomIndex from './RoomIndex'
import _ from 'lodash'

export default class RoomContainer extends React.Component {
  constructor(props) {
    super(props)
  }

  reFilter(filters) {
    const formattedDates = {arrive: filters.dates.arrive.format('MM/DD/YYYY'), depart: filters.dates.depart.format('MM/DD/YYYY')}
    browserHistory.push({
      pathname: '/locations/'+this.props.routeParams.location+'/stay',
      query: formattedDates
    })
  }

  render() {
    return <RoomIndex
      rooms={this.props.rooms}
      routeParams={this.props.routeParams}
      query={this.props.location.query}
      onFilterChange={this.reFilter.bind(this)} />
  }
}
