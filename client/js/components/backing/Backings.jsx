import React, {PropTypes} from 'react'
import { Router, Route, browserHistory, IndexRoute } from 'react-router'
import ScheduledBackings from './ScheduledBackings'
import ApolloClient from 'apollo-client'
import { ApolloProvider } from 'react-apollo'

const client = new ApolloClient();

export default class Backings extends React.Component {
  static propTypes = {
      resourceID: PropTypes.number.isRequired
  }

  render() {

    const {resourceID} = this.props

    return (
      <ApolloProvider client={client}>
        <ScheduledBackings rid={resourceID} client={client} />
      </ApolloProvider>
    )
  }
}
