import React, {PropTypes} from 'react'
import RoomCard from './RoomCard'
import DateRangeSelector from './DateRangeSelector'

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
        <div className="date-range-row">
          <DateRangeSelector onChange={this.onDateRangeChange.bind(this)} query={this.props.query} {...this.props.query} />
        </div>
        <div className="row room-card-container">{roomCards}</div>
      </div>
    )
  }
}
