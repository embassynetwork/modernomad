import axios from 'axios'
import React, {PropTypes} from 'react'
import qs from 'qs'
import RoomIndex from './RoomIndex'
import RoomDetail from './RoomDetail'
import _ from 'lodash'
import moment from 'moment'
import makeParam from '../generic/Utils'
import DATEFORMAT from './constants'


class RoomIndexOrDetailWithoutQuery extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      rooms:this.props.rooms || [],
      errorMsg: null
    }
    this.location_name = props.match.params.location
    let search = props.location.search.slice(1)
    this.query = qs.parse(search)
  }

  componentWillMount() {
    // Rooms need to be fetched if the page didn't start out with any rooms
    // which happens when going from individual room to list view.
    if (this.props.rooms == undefined) {
      this.fetchRooms(null)
    }
  }

  fetchRooms(dates) {
    let paramObj = dates ? {params: dates} : {}
    let jsonUrl = `/locations/${this.location_name}/json/room`
    this.setState({ errorMsg: null })
    axios.get(jsonUrl, paramObj)
      .then(res => {
        const rooms = res.data;
        this.setState({ rooms: rooms });
      }).catch((error) => {
        this.setState({ errorMsg: 'An error occurred, we\'ll take a look at it' })
      })
  }

  renderSubComponent() {
    const sharedProps = {
      ...this.props,
      onFilterChange: this.reFilter.bind(this),
      location_name: this.location_name,
      query: this.query,
      errorMsg: this.state.errorMsg
    }
    return <RoomIndex {...sharedProps} rooms={this.state.rooms} />
  }

  reFilter(filters) {
    const formattedDates = {
      arrive: filters.dates.arrive.format(DATEFORMAT),
      depart: filters.dates.depart.format(DATEFORMAT)
    }
    var path = `/locations/${this.location_name}/stay/`
    this.fetchRooms(formattedDates)

    let location = {
      pathname: path,
      search: makeParam(formattedDates)
    }

    this.props.history.push(location)
  }

  render() {
    return (
      <div>
        {this.renderSubComponent()}
      </div>
    )
  }
}

export default RoomIndexOrDetailWithoutQuery
