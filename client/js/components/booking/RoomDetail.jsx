import React, {PropTypes} from 'react'
import moment from 'moment'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'
import BookingForm from './BookingForm'
import { Link } from 'react-router'
import _ from 'lodash'
import nl2br from 'react-nl2br'
import { isFullyAvailable } from '../../models/Availabilities'

export default class RoomDetail extends React.Component {
  static propTypes = {
    room: PropTypes.object.isRequired,
    onFilterChange: PropTypes.func.isRequired,
    networkLocation: PropTypes.object
  }

  hasDateQuery() {
    return this.props.query.arrive
  }

  roomIsAvailable() {
    if (this.hasDateQuery()) {
      return isFullyAvailable(this.props.room.availabilities)
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

    // destructuring
    const { query, onFilterChange } = this.props
    // const query = this.props.query
    // const onFilterChange = this.props.onFilterChange

    return (
      <div className="container room-detail">
        <Link to={this.indexLinkDetails()}><i className="fa fa-chevron-left"></i> Back to Rooms</Link>
        <h1>{room.name}</h1>
        <div className="row">
          <div className="col-md-8">
            <div className="room-image-panel">
              <img className="room-image img-responsive" src={"/media/"+room.image} />
            {/*room.img && <ImageCarousel img={room.img} />*/}
            </div>
            <p className="room-summary">{nl2br(room.description)}</p>
          </div>
          <div className="col-md-4">
            <div className="panel">
              <BookingForm 
                networkLocation={this.networkLocation}
                room={room}
                datesAvailable={this.roomIsAvailable()}
                {...this.props}
                query={query} {/* this might be redundent because of the object-spread on the line above*/}
                onFilterChange={onFilterChange}
              />
            </div>
          </div>
        </div>
      </div>
    )

  }
}
