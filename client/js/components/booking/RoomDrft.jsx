import React, {PropTypes} from 'react'
// import { browserHistory } from 'react-router'
import RoomDrftIndex from './RoomDrftIndex'
import RoomDetail from './RoomDetail'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import _ from 'lodash'
import moment from 'moment'
import Loader from '../generic/Loader'

const resourcesQuery = gql`
query AllResourcesForLocation($arrive: DateTime!, $depart: DateTime!) {
  allLocations {
    edges {
      node {
        name
        slug
        resources(hasFutureDrftCapacity: true){
          id
          rid
          name
          image
          defaultRate
          hasFutureDrftCapacity
          acceptDrftTheseDates(arrive: $arrive, depart: $depart)
          availabilities(arrive: $arrive, depart: $depart) {
            date
            quantity
          }
        }
      }
    }
  }
}
`;

class RoomDrftIndexOrDetailWithoutQuery extends React.Component {
  constructor(props) {
    super()
  }

  renderSubComponent() {
    const routeParams = this.props.routeParams
    const child = this.props.children
    const sharedProps = {
      ...this.props,
      onFilterChange: this.reFilter.bind(this),
      query: this.props.location.query,
      loading: this.props.data.loading
    }

    if (!!child) {
      const roomID = child.props.routeParams.id
      const room = this.oneResource(roomID)

      if (room) {
        return (
          <RoomDetail {...sharedProps} room={room}>
            {this.props.children}
          </RoomDetail>
        )
      } else {
        return null;
      }
    } else {
      return <RoomDrftIndex {...sharedProps} rooms={this.allResources()} />
    }
  }

  reFilter(filters) {
    const formattedDates = {arrive: filters.dates.arrive.format('MM/DD/YYYY'), depart: filters.dates.depart.format('MM/DD/YYYY')}
    var path = '/drft/'

    if (this.props.params.id) {
      path = path + 'room/' + this.props.params.id
    }

    browserHistory.push({
      pathname: path,
      query: formattedDates
    })
  }

  locationData() {
    const queryResults = this.props.data.allLocations
    if (queryResults && queryResults.edges.length > 0) {
      return queryResults.edges
    } else {
      return null
    }
  }

  allResources() {
    const location = this.locationData()
    if (location) {
      return location
    } else {
      return []
    }
  }

  oneResource(id) {
    return _.find(this.allResources(), {rid: parseInt(id)})
  }

  render() {
    return (
      <Loader loading={this.props.data.loading}>
        {this.renderSubComponent()}
      </Loader>
    )
  }
}

const RoomDrftIndexOrDetail = graphql(resourcesQuery, {
  options: (props) => {
    const formatString = 'Y-MM-DTHH:mm:ss.ms'
    const parseFormat = 'MM/DD/YYYY'
    const query = props.location.query
    const arrive = query.arrive ? moment(query.arrive, parseFormat) : moment().startOf('day')
    const depart = query.depart ? moment(query.depart, parseFormat) : arrive.clone().add(7, 'days')

    return {
      variables: {
        arrive: arrive.format(formatString),
        depart: depart.format(formatString)
      }
    }
  }
})(RoomDrftIndexOrDetailWithoutQuery)
export default RoomDrftIndexOrDetail
