import React, {PropTypes} from 'react'
import { BrowserRouter, Route } from 'react-router-dom'
import RoomIndexOrDetail from './RoomIndexOrDetail'
import RoomDrft from './RoomDrft'
import RoomDetail from './RoomDetail'

class DummyRoomDetail extends React.Component {
  render() {
    return <div>here is the detail</div>
  }
}

// Kind reminder of what lifecycle methods exists
// https://gist.github.com/bvaughn/923dffb2cd9504ee440791fade8db5f9

class RoomBookingRoutes extends React.Component {
  render() {
    return (
      <BrowserRouter>
        <div>
          <Route
            path="/drft/"
            component={RoomDrft}
            drftBalance={this.props.drftBalance}
            isAdmin={this.props.isAdmin}
          />
          <Route
            exact path="/locations/:location/stay/"
            render={(props) => {
              return <RoomIndexOrDetail
                {...props}
                rooms={this.props.rooms}
                isAdmin={this.props.isAdmin}
              />
            }}
          />
          <Route
            path="/locations/:location/stay/room/:id"
            render={(props) => <RoomDetail
              {...props}
              room={this.props.room}
              fees={this.props.fees}
              drftBalance={this.props.drftBalance}
            />}
          />
        </div>
      </BrowserRouter>
    )
  }
}

export default class RoomBooking extends React.Component {
  render() {
    return (
        <RoomBookingRoutes
          drftBalance={this.props.user_drft_balance}
          isAdmin={this.props.is_house_admin}
          room={this.props.room}
          rooms={this.props.rooms}
          fees={this.props.fees}
        />
    )
  }
}
