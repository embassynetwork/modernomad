import axios from 'axios'
import React, {PropTypes} from 'react'
import moment from 'moment'
import queryString from 'query-string'

import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'
import BookingForm from './BookingForm'
import Loader from '../generic/Loader'
import { Link } from 'react-router-dom'
import _ from 'lodash'
import nl2br from 'react-nl2br'
import { isFullyAvailable } from '../../models/Availabilities'
import makeParam from '../generic/Utils'

export default class RoomDetail extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      room: this.props.room,
      loading: false
    };
    this.pk = props.match.params.id
  }

  componentWillMount() {
    if (this.props.room == undefined) {
      this.setState({ loading: true })
      this.fetchRoom({})
    }
  }

  fetchRoom(filters) {
    let formattedDates = {}
    if (!_.isEmpty(filters)) {
      formattedDates['arrive'] = filters.dates.arrive.format('MM/DD/YYYY')
      formattedDates['depart'] = filters.dates.depart.format('MM/DD/YYYY')
    }

    var path = `/locations/${this.props.location_name}/stay/room/${this.pk}`
    // need arrive and depart too.
    axios.get(`/locations/${this.props.location_name}/json/room/${this.pk}`)
      .then(res => {
        const room = res.data
        this.setState({ room: room })
        this.setState({ loading: false })
    });

    let urlLocation = {
      pathname: path,
      search: makeParam(formattedDates)
    }

    this.props.history.push(urlLocation)
  }

  roomIsAvailable() {
    if (this.props.query) {
      return isFullyAvailable(this.state.room.availabilities)
    }
    return false
  }

  indexLinkDetails() {
    return {
      pathname: `/locations/${this.props.location_name}/stay/`,
      query: this.props.query
    }
  }

  render() {
    const isDetail = true
    let isLoading = this.state.loading

    return (
      <Loader loading={this.state.loading}>
        { !isLoading ?
          (<div className="container room-detail">
          <Link to={this.indexLinkDetails()}><i className="fa fa-chevron-left"></i> Back to Rooms</Link>
          <h1>{this.state.room.name}</h1>
          <div className="row">
            <div className="col-md-8">
              <div className="room-image-panel">
                <img className="room-image img-responsive" src={this.state.room.image} />
              {/*room.img && <ImageCarousel img={room.img} />*/}
              </div>
              <p className="room-summary">{nl2br(this.state.room.description)}</p>
            </div>
            <div className="col-md-4">
              <div className="panel">
                <BookingForm
                  {...this.props}
                  room={this.state.room}
                  datesAvailable={this.roomIsAvailable()}
                  onFilterChange={this.fetchRoom.bind(this)}
                  drftBalance={this.props.drftBalance}
                />
              </div>
            </div>
          </div>
        </div>) : (null)
      }
      </Loader>
    )
  }
}
