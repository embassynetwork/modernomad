import React, {PropTypes} from 'react'
import RoomCard from './RoomCard'
import DateRangeSelector from './DateRangeSelector'
import AvailabilityMatrix from './AvailabilityMatrix'
import { FormGroup, Checkbox, Button, Nav, NavItem } from 'react-bootstrap';
import { isFullyAvailable } from '../../models/Availabilities'

export default class RoomCards extends React.Component {
  static propTypes = {
    rooms: PropTypes.array.isRequired
  }

  render() {
    const { rooms, drft, routeParams, query, loading } = this.props

    if (rooms.length > 0) {
      return (
        <div className="row" id="room-cards">
          {rooms.map(room => <RoomCard key={room.id} drft={drft} routeParams={routeParams} query={query} {...room} /> )}
        </div>
      )
    } 
    
    if (loading) return null 
    
    const msg = drft
      ? "Sorry, this location has rooms that accept Ɖ but none of those rooms match your search"
      : "Sorry, no rooms match your search"
    
    return (
      <div className="no-data">{msg}</div>
    )
  }
}

