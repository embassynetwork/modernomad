import React, {PropTypes} from 'react'
import DateRangeSelector from './DateRangeSelector'
import AvailabilityMatrix from './AvailabilityMatrix'
import { FormGroup, Checkbox, Button, Nav, NavItem } from 'react-bootstrap';
import { isFullyAvailable } from '../../models/Availabilities'
import RoomCards from './RoomCards'

export default class RoomDrftIndex extends React.Component {
  static propTypes = {
    rooms: PropTypes.array.isRequired,
    onFilterChange: PropTypes.func.isRequired
  }

  constructor(props) {
    super(props)

    this.state = {activeKey: 1, showAvailabilityTable: false}
  }

  onDateRangeChange(dates) {
    this.props.onFilterChange({dates: dates})
  }

  handleSelect(selectedKey) {
    this.setState({activeKey: selectedKey})
    if (selectedKey == 1) {
      this.setState({showAvailabilityTable: false})
    } else { this.setState({showAvailabilityTable: true})}
  }

  hasDateQuery() {
    return this.props.query.arrive
  }

  displayableRooms(rooms) {
    if (this.hasDateQuery()) {
      return _.filter(rooms, (room) => {
        return isFullyAvailable(room.availabilities)
      })
    } else {
      return rooms
    }
  }

  routeParams(room) {
    return {location: room.slug}
  }

  renderLocationRoomCards() {
    return this.props.rooms.reverse().map((room) => {
      if (room.node.resources.length) {
        return (
          <div key={room.node.name}>
            <a href={'/locations/'+room.node.slug} target='_blank'>
              <h2 className="location-heading">{room.node.name}</h2>
            </a>
            <RoomCards loading={this.props.loading} rooms={this.displayableRooms(room.node.resources)} drft={true} routeParams={this.routeParams(room.node)} query={this.props.query} route={this.props.route} />
          </div>
        )
      }
    })
  }

  renderLocationAvailabilities() {
    return this.props.rooms.map((room) => {
      if (room.node.resources.length) {
        return (
          <div key={room.node.name}>
            <a href={'/locations/'+room.node.slug} target='_blank'>
              <h2>{room.node.name}</h2>
            </a>
            <AvailabilityMatrix rooms={room.node.resources} drft={true} routeParams={this.routeParams(room.node)} query={this.props.query}></AvailabilityMatrix>
          </div>
        )
      }
    })
  }

  render() {
    return (
      <div>
        <div className="date-range-row container">
          <DateRangeSelector
            onChange={this.onDateRangeChange.bind(this)}
            maxLength={this.props.networkLocation ? this.props.networkLocation.maxBookingDays : null}
            inputClass='input-lg'
            {...this.props.query} />
          {/*}<div className="row room-type-row">
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
          </div>*/}
        </div>
        <div className="room-card-container">
          <div className="container">
            <div className="row availability-table-toggle">
              <Nav bsStyle="pills" className="pull-right" activeKey={this.state.activeKey} onSelect={this.handleSelect.bind(this)}>
                <NavItem eventKey={1} title="Room Grid"><i className="fa fa-th"></i></NavItem>
                <NavItem eventKey={2} title="Availability Matrix"><i className="fa fa-list"></i></NavItem>
              </Nav>
            </div>
            {
              !this.state.showAvailabilityTable ?
              this.renderLocationRoomCards() :
              this.renderLocationAvailabilities()
            }
          </div>
        </div>
      </div>
    )
  }
}
