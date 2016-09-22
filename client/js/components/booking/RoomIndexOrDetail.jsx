import React, {PropTypes} from 'react'
import RoomContainer from './RoomContainer'
import RoomDetail from './RoomDetail'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import _ from 'lodash'

const resourcesQuery = gql`
{
  allResources(location: "TG9jYXRpb25Ob2RlOjE2") {
    edges {
      node {
        id
        rid
        name
        description
        summary
        image
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

const RoomIndexOrDetail = graphql(resourcesQuery)(RoomIndexOrDetailWithoutQuery)
export default RoomIndexOrDetail
