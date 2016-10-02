import React, {PropTypes} from 'react'
import moment from 'moment'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'
import BookingForm from './BookingForm'

export default class RoomDetail extends React.Component {
  static propTypes = {
    room: PropTypes.object.isRequired,
    onFilterChange: PropTypes.func.isRequired
  }

  hasDateQuery() {
    return this.props.query.arrive
  }

  roomIsAvailable() {
    if (this.hasDateQuery()) {
      return !!_.find(this.props.room.availabilities, {quantity: 0})
    } else {
      return false
    }
  }

  render() {
    const room = this.props.room
    const isDetail = true

    return (
      <div className="container">
        <h1>{room.name}</h1>
        <p>{room.summary}</p>
        <div className="row">
          <div className="col-sm-8">
            <img className="room-image" src={"/media/"+room.image} />
            {/*room.img && <ImageCarousel img={room.img} />*/}
          </div>
          <div className="col-sm-4 panel">
            <BookingForm room={room} datesAvailable={this.roomIsAvailable()} query={this.props.query} onFilterChange={this.props.onFilterChange} />
          </div>
        </div>
      </div>
    )

  }
}
