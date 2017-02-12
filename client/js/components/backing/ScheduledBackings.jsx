import React, {PropTypes} from 'react'
import { graphql } from 'react-apollo'
import ScheduledBackingsTable from './ScheduledBackingsTable'
import BackingFormWithData from './BackingForm'
import gql from 'graphql-tag'
import _ from 'lodash'
import moment from 'moment'
import Loader from '../generic/Loader'

const backingsQuery = gql`
query ScheduledFutureBackings($rid: ID!) {
  resource(id:$rid) {
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

class ScheduledBackingsWithoutQuery extends React.Component {
  static propTypes = {
      rid: PropTypes.number.isRequired,
      parent: PropTypes.object.isRequired
  }

  renderSubComponent() {
    const {rid, data, parent} = this.props
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

const ScheduledBackings = graphql(backingsQuery, {
  // defines required arguments - but by default graphql will look at the props
    // of the parent component, which, here, directly has a prop called rid already.
  // options: { variables: { rid: rid } },
})(ScheduledBackingsWithoutQuery)

export default ScheduledBackings
