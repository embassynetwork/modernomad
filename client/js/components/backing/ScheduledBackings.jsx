import React, {PropTypes} from 'react'
import { graphql } from 'react-apollo'
import ScheduledBackingsTable from './ScheduledBackingsTable'
import gql from 'graphql-tag'
import _ from 'lodash'
import moment from 'moment'
import Loader from '../generic/Loader'

const backingsQuery = gql`
query AllBackings {
  allBackings(first:10) {
    edges {
      node {
        resourceId
        id
      }
    }
  }
}
`;

class ScheduledBackingsWithoutQuery extends React.Component {
  constructor(props) {
    super()
  }

  renderSubComponent() {
    if (this.props.data.loading) {
      return null
    } else {
      return (
        <ScheduledBackingsTable backings={this.backingData()}/>
      )
    }
  }

  backingData() {
    const queryResults = this.props.data.allBackings
    if (queryResults && queryResults.edges.length > 0) {
      return queryResults.edges
    } else {
      return null
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
  // defines required arguments
})(ScheduledBackingsWithoutQuery)
export default ScheduledBackings
