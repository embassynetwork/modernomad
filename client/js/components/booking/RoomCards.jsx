import React, {PropTypes} from 'react'
import RoomCard from './RoomCard'
import DateRangeSelector from './DateRangeSelector'
import AvailabilityMatrix from './AvailabilityMatrix'
import { FormGroup, Checkbox, Button, Nav, NavItem } from 'react-bootstrap';
import { isFullyAvailable } from '../../models/Availabilities'

class RoomCards extends React.Component {
  static propTypes = {
    rooms: PropTypes.array.isRequired
  }

  renderRoomCards() {
    return this.props.rooms.map((room) => {
      return <RoomCard
        key={room.id}
        drft={this.props.drft}
        location={this.props.location}
        match={this.props.match}
        isAdmin={this.props.isAdmin}
        {...room}
        {...this.props}
      />
    })
  }

  render() {
    if (this.props.errorMsg) {
      return <div className="no-data">{this.props.errorMsg}</div>
    }
    else if (this.props.rooms.length > 0) {
      return (
        <div className="row" id="room-cards">
          {this.renderRoomCards()}
        </div>
      )
    }
    else {
      if (this.props.loading) {
        return null
      } else {
        if (this.props.drft){
          return <div className="no-data">Sorry, this location has rooms that accept Ɖ but none of those rooms match your search</div>
        }
        else {
          return <div className="no-data">Sorry, no rooms match your search</div>
        }
      }
    }
  }
}
export default RoomCards
