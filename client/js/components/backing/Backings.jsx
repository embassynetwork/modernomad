import React, {PropTypes} from 'react'
import { Router, Route, browserHistory, IndexRoute } from 'react-router'
import ScheduledBackings from './ScheduledBackings'
import ApolloClient from 'apollo-client'
import { ApolloProvider } from 'react-apollo'
import BackingFormWithData from './BackingForm'
import CurrentBacking from './CurrentBacking'

const client = new ApolloClient();

export default class Backings extends React.Component {
  static propTypes = {
      resourceID: PropTypes.number.isRequired,
      allUsers: PropTypes.array.isRequired
  }

  constructor(props) {
    super(props)
    // gets set when graphql queries execute
    this.state = {scheduledBackingsData: {}, currentBackersData: {}}
  }

  refetch() {
      this.state.scheduledBackingsData.refetch()
      this.state.currentBackersData.refetch()
  }

  render() {

    const {resourceID, allUsers} = this.props
    return (
      <ApolloProvider client={client}>
        <div>
          <hr />
          <h3>Backings</h3>
          <CurrentBacking resourceID={resourceID} parent={this}/>
          <ScheduledBackings resourceID={resourceID} parent={this} allUsers={allUsers}/>
          <BackingFormWithData resource={resourceID} parent={this}/>
        </div>
      </ApolloProvider>
    )
  }
}
