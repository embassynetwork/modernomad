import React, {PropTypes} from 'react'
import RoomCard from './RoomCard'
import DateRangeSelector from './DateRangeSelector'
import AvailabilityMatrix from './AvailabilityMatrix'
import { FormGroup, Checkbox, Button, Nav, NavItem } from 'react-bootstrap';
import { isFullyAvailable } from '../../models/Availabilities'
import RoomCards from './RoomCards'

export default class RoomIndex extends React.Component {
  static propTypes = {
    rooms: PropTypes.array.isRequired,
    onFilterChange: PropTypes.func.isRequired,
    networkLocation: PropTypes.object
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

  displayableRooms() {
    if (this.hasDateQuery()) {
      return _.filter(this.props.rooms, (room) => {
        return isFullyAvailable(room.availabilities)
      })
    } else {
      return this.props.rooms
    }
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
              <RoomCards loading={this.props.loading} rooms={this.displayableRooms()} routeParams={this.props.routeParams} query={this.props.query} route={this.props.route}/> :
              <AvailabilityMatrix rooms={this.props.rooms} routeParams={this.props.routeParams} query={this.props.query}></AvailabilityMatrix>
            }
          </div>
        </div>
      </div>
    )
  }
}
