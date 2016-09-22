import React, {PropTypes} from 'react'
import { Router, Route, browserHistory, IndexRoute } from 'react-router'
import RoomIndexOrDetail from './RoomIndexOrDetail'
import ApolloClient from 'apollo-client'
import { ApolloProvider } from 'react-apollo'

const client = new ApolloClient();

class RoomBookingRoutes extends React.Component {
  render() {
    return (
      <Router history={browserHistory}>
        <Route path="/locations/:location/stay" component={RoomIndexOrDetail} />
        <Route path="/locations/:location/stay/room/:id" component={RoomIndexOrDetail} />
      </Router>
    )
  }
}

export default class RoomBooking extends React.Component {
  render() {
    return (
      <ApolloProvider client={client}>
        <RoomBookingRoutes />
      </ApolloProvider>
    )
  }
}
