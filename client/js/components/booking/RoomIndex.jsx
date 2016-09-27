import React, {PropTypes} from 'react'
import RoomCard from './RoomCard'
import DateRangeSelector from './DateRangeSelector'
import { FormGroup, Checkbox, Button } from 'react-bootstrap';

export default class RoomIndex extends React.Component {
  static propTypes = {
    rooms: PropTypes.array.isRequired,
    onFilterChange: PropTypes.func.isRequired
  }

  onDateRangeChange(dates) {
    this.props.onFilterChange({dates: dates})
  }

  render() {
    const roomCards = this.props.rooms.map((room) => {
      // return <RoomCard key={room.id} room={room.name} img={room.img} />
      return <RoomCard key={room.id} routeParams={this.props.routeParams} query={this.props.query} {...room} />
    })

    return (
      <div>
        <div className="date-range-row container">
          <DateRangeSelector onChange={this.onDateRangeChange.bind(this)} query={this.props.query} {...this.props.query} />
          <div className="row room-type-row">
            <div className="col-md-2 col-sm-4"><h5>Room Type</h5></div>
            <div className="col-md-2 col-sm-4">
              <Checkbox className="btn btn-default btn-block room-type-btn">
                <i className="fa fa-lock"></i> Private Room
              </Checkbox>
            </div>
            <div className="col-md-2 col-sm-4">
              <Checkbox className="btn btn-default btn-block room-type-btn">
                <i className="fa fa-unlock-alt"></i> Shared Room
              </Checkbox>
            </div>
          </div>
        </div>
        <div className="room-card-container">
          <div className="container">
            <div className="row">{roomCards}</div>
          </div>
        </div>
      </div>
    )
  }
}
