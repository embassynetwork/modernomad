import React, {PropTypes} from 'react'
import RoomCard from './RoomCard'
import DateRangeSelector from './DateRangeSelector'

export default class RoomIndex extends React.Component {
  static propTypes = {
    rooms: PropTypes.array.isRequired,
    onChange: PropTypes.func.isRequired
  }

  render() {
    const roomCards = this.props.rooms.map((room) => {
      // return <RoomCard key={room.id} room={room.name} img={room.img} />
      return <RoomCard key={room.id} {...room} />
    })

    return (
      <div>
        <DateRangeSelector onChange={this.props.onChange} />
        <div className="row">{roomCards}</div>
      </div>
    )
  }
}
