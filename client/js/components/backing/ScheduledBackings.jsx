import React, {PropTypes} from 'react'
import { graphql } from 'react-apollo'
import ScheduledBackingsTable from './ScheduledBackingsTable'
import gql from 'graphql-tag'
import _ from 'lodash'
import moment from 'moment'
import Loader from '../generic/Loader'

const backingsQuery = gql`
query ScheduledFutureBackings($resourceID: ID!) {
  resource(id:$resourceID) {
    name,
    scheduledFutureBackings {
      id,
      users {
        edges {
          node {
            id,
            firstName,
            lastName,
            username
          }
        }
      },
      start
    }
  }
}
`;

class ScheduledBackingsWithoutData extends React.Component {
  static propTypes = {
      resourceID: PropTypes.number.isRequired,
      parent: PropTypes.object.isRequired
  }

  renderSubComponent() {
    const {resourceID, data, parent} = this.props
    parent.state.scheduledBackingsData = this.props.data
    console.log('parent.state', parent.state) 

    if (data.loading) {
      return null
    } else {
      return (
        <div>
          <ScheduledBackingsTable backings={this.backingData()}/>
        </div>
      )
    }
  }

  backingData() {
    const queryResults = this.props.data.resource

    if (queryResults && queryResults.scheduledFutureBackings.length > 0) {
        return queryResults.scheduledFutureBackings
    } else {
        return []
    }
  }

  render() {
    return (
      <Loader loading={this.props.data.loading}>
        {this.renderSubComponent()}
      </Loader>
    )
  }
}

const ScheduledBackings = graphql(backingsQuery)(ScheduledBackingsWithoutData) 
export default ScheduledBackings
