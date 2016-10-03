import React, {PropTypes} from 'react'
import moment from 'moment'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'
import BookingForm from './BookingForm'
import { Link } from 'react-router'
import _ from 'lodash'

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
      return !_.find(this.props.room.availabilities, {quantity: 0})
    } else {
      return false
    }
  }

  indexLinkDetails() {
    return {
      pathname: `/locations/${this.props.routeParams.location}/stay/`,
      query: this.props.query
    }
  }

  render() {
    const room = this.props.room
    const isDetail = true

    return (
      <div className="container room-detail">
        <Link to={this.indexLinkDetails()}><i className="fa fa-chevron-left"></i> Back to Rooms</Link>
        <h1>{room.name}</h1>
        <p className="room-summary">{room.summary}</p>
        <div className="row">
          <div className="col-sm-8">
            <div className="panel room-image-panel">
              <img className="room-image img-responsive" src={"/media/"+room.image} />
            {/*room.img && <ImageCarousel img={room.img} />*/}
            </div>
          </div>
          <div className="col-sm-4 panel">
            <BookingForm room={room} {...this.props} datesAvailable={this.roomIsAvailable()} query={this.props.query} onFilterChange={this.props.onFilterChange} />
          </div>
        </div>
      </div>
    )

  }
}
