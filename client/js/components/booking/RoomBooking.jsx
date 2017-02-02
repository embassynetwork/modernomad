import React, {PropTypes} from 'react'
import { Router, Route, browserHistory, IndexRoute } from 'react-router'
import RoomIndexOrDetail from './RoomIndexOrDetail'
import RoomDrft from './RoomDrft'
import RoomDetail from './RoomDetail'
import ApolloClient from 'apollo-client'
import { ApolloProvider } from 'react-apollo'

const client = new ApolloClient();

class DummyRoomDetail extends React.Component {
  render() {
    return <div>here is the detail</div>
  }
}

class RoomBookingRoutes extends React.Component {
  render() {
    return (
      <Router history={browserHistory}>
        <Route path="/drft/" component={RoomDrft} drftBalance={this.props.drftBalance} isAdmin={this.props.isAdmin}>
        </Route>
        <Route path="/locations/:location/stay/" component={RoomIndexOrDetail} drftBalance={this.props.drftBalance} isAdmin={this.props.isAdmin}>
          <Route path="room/:id" component={DummyRoomDetail} />
        </Route>
      </Router>
    )
  }
}

export default class RoomBooking extends React.Component {
  render() {
    return (
      <ApolloProvider client={client}>
        <RoomBookingRoutes drftBalance={this.props.request_user_drft_balance} isAdmin={this.props.is_user_admin}/>
      </ApolloProvider>
    )
  }
}
