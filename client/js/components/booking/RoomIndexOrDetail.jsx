import axios from 'axios'
import React, {PropTypes} from 'react'
import RoomIndex from './RoomIndex'
import RoomDetail from './RoomDetail'
import _ from 'lodash'
import moment from 'moment'
import makeParam from '../generic/Utils'


class RoomIndexOrDetailWithoutQuery extends React.Component {
  constructor(props) {
    super(props)
    this.state = { rooms:this.props.rooms || [] };
  }

  componentWillMount() {
    // Rooms need to be fetched if the page didn't start out with any rooms
    // which happens when going from individual room to list view.
    if (this.props.rooms == undefined) {
      axios.get(`/locations/${this.props.location_name}/json/room/`)
        .then(res => {
          const rooms = res.data;
          this.setState({ rooms: rooms });
      });
    }
  }

  renderSubComponent() {
    const sharedProps = {
      ...this.props,
      onFilterChange: this.reFilter.bind(this),
    }
    return <RoomIndex {...sharedProps} rooms={this.state.rooms} />
  }

  reFilter(filters) {
    const formattedDates = {
      arrive: filters.dates.arrive.format('MM/DD/YYYY'),
      depart: filters.dates.depart.format('MM/DD/YYYY')
    }
    var path = `/locations/${this.props.location_name}/stay/`

    let jsonUrl = `/locations/${this.props.location_name}/json/room`
    axios.get(jsonUrl, {params: formattedDates})
      .then(res => {
        const rooms = res.data;
        this.setState({ rooms: rooms });
    })

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
