import React, {PropTypes} from 'react'
import { browserHistory } from 'react-router'
import RoomContainer from './RoomContainer'
import RoomDetail from './RoomDetail'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import _ from 'lodash'
import moment from 'moment'
import Loader from 'react-loader-advanced'

const resourcesQuery = gql`
query AllResourcesForLocation($locationSlug: String!, $arrive: DateTime!, $depart: DateTime!) {
  allResources(location_Slug: $locationSlug) {
    edges {
      node {
        id
        rid
        name
        description
        summary
        image
        defaultRate
        availabilities(arrive: $arrive, depart: $depart) {
          date
          quantity
        }
        location {
          id
        }
      }
    }
  }
}
`;

class RoomIndexOrDetailWithoutQuery extends React.Component {
  renderSubComponent() {
    const routeParams = this.props.routeParams

    if (routeParams.id) {
      return <RoomDetail {...this.props} room={this.oneResource(routeParams.id)} onFilterChange={this.reFilter.bind(this)} query={this.props.location.query} />
    } else {
      return <RoomContainer {...this.props} rooms={this.allResources()} />
    }
  }

  reFilter(filters) {
    const formattedDates = {arrive: filters.dates.arrive.format('MM/DD/YYYY'), depart: filters.dates.depart.format('MM/DD/YYYY')}
    browserHistory.push({
      pathname: '/locations/'+this.props.routeParams.location+'/stay/room/'+this.props.routeParams.id,
      query: formattedDates
    })
  }

  allResources() {
    const queryResults = this.props.data.allResources
    if (queryResults) {
      return _.map(queryResults.edges, 'node')
    } else {
      return []
    }
  }

  oneResource(id) {
    return _.find(this.allResources(), {rid: parseInt(id)})
  }

  render() {
    return (
      <Loader show={this.props.data.loading}>
        {this.renderSubComponent()}
      </Loader>
    )
  }
}

const RoomIndexOrDetail = graphql(resourcesQuery, {
  options: (props) => {
    const formatString = 'Y-MM-DTHH:mm:ss.ms'
    const parseFormat = 'MM/DD/YYYY'
    const query = props.location.query
    const arrive = query.arrive ? moment(query.arrive, parseFormat) : moment()
    const depart = query.depart ? moment(query.depart, parseFormat) : arrive.clone().add(7, 'days')

    return {
      variables: {
        locationSlug: props.routeParams.location,
        arrive: arrive.format(formatString),
        depart: depart.format(formatString)
      }
    }
  }
})(RoomIndexOrDetailWithoutQuery)
export default RoomIndexOrDetail
