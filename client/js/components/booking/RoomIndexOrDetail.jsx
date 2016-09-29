import React, {PropTypes} from 'react'
import RoomContainer from './RoomContainer'
import RoomDetail from './RoomDetail'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import _ from 'lodash'

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
        bookabilities(arrive: $arrive, depart: $depart) {
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
      return <RoomDetail {...this.props} room={this.oneResource(routeParams.id)} />
    } else {
      return <RoomContainer {...this.props} rooms={this.allResources()} />
    }
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
    return this.allResources()[0]
  }

  render() {
    const queryResults = this.props.data.allResources

    if (queryResults) {
      return this.renderSubComponent();
    } else {
     return <div>loading</div>
    }

    return this.renderSubComponent();
  }
}

const RoomIndexOrDetail = graphql(resourcesQuery, {
  options: (props) => {
    return {
      variables: {
        locationSlug: props.routeParams.location,
        arrive: "2016-09-03T20:56:35.450686",
        depart: "2016-09-05T20:56:35.450686"
      }
    }
  }
})(RoomIndexOrDetailWithoutQuery)
export default RoomIndexOrDetail
