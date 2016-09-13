import React, {PropTypes} from 'react'
import { Router, Route, browserHistory, IndexRoute } from 'react-router'
import RoomContainer from './RoomContainer'
import RoomDetail from './RoomDetail'


export default class RoomBooking extends React.Component {

  render() {

    return (
      <Router history={browserHistory}>
        <Route path="/locations/:location/stay" component={RoomContainer} />
        <Route path="/locations/:location/stay/room/:id" component={RoomDetail} />
      </Router>
    )

  }
}
