import React, {PropTypes} from 'react'
import { Router, Route, browserHistory, IndexRoute } from 'react-router'
import ScheduledBackings from './ScheduledBackings'
import ApolloClient from 'apollo-client'
import { ApolloProvider } from 'react-apollo'
import BackingFormWithData from './BackingForm'

const client = new ApolloClient();

export default class Backings extends React.Component {
  static propTypes = {
      resourceID: PropTypes.number.isRequired
  }

  constructor(props) {
    super(props)
    // set when graphql queries execute
    this.state = {scheduledBackingsData: {}, currentBackingData: {}}
  }
  
  refetch() {
      this.state.scheduledBackingsData.refetch()
  }

  render() {

    const {resourceID} = this.props
    return (
      <ApolloProvider client={client}>
        <div>
          <ScheduledBackings rid={resourceID} parent={this}/>
          <BackingFormWithData resource={resourceID} parent={this}/>
        </div>
      </ApolloProvider>
    )
  }
}
