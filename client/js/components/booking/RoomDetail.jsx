import axios from 'axios'
import React, {PropTypes} from 'react'
import moment from 'moment'
import qs from 'qs'

import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'
import BookingForm from './BookingForm'
import Loader from '../generic/Loader'
import { Link } from 'react-router-dom'
import _ from 'lodash'
import nl2br from 'react-nl2br'
import { isFullyAvailable } from '../../models/Availabilities'
import makeParam from '../generic/Utils'
import DATEFORMAT from './constants'

export default class RoomDetail extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      room: this.props.room,
      loading: false
    };

    this.pk = props.match.params.id
    this.location_name = props.match.params.location
    let search = props.location.search.slice(1)
    this.query = qs.parse(search)
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
      formattedDates['arrive'] = filters.dates.arrive.format(DATEFORMAT)
      formattedDates['depart'] = filters.dates.depart.format(DATEFORMAT)
      this.query = formattedDates
    }

    var path = `/locations/${this.location_name}/stay/room/${this.pk}`
    axios.get(`/locations/${this.location_name}/json/room/${this.pk}`)
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
    if (!_.isEmpty(this.query)) {
      return isFullyAvailable(this.state.room.availabilities)
    }
    return false
  }

  indexLinkDetails() {
    return {
      pathname: `/locations/${this.location_name}/stay/`,
      query: this.query
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
                  location_name={this.location_name}
                  query={this.query}
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
