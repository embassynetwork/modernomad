import React, {PropTypes} from 'react'
import { Table } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import moment from 'moment'


export default class AvailabilityMatrix extends React.Component {
  static propTypes = {
    rooms: PropTypes.array.isRequired
  }

  constructor(props) {
    super(props)
    this.dates = ['today', 'tomorrow']
  }

  detailUrl(id) {
    return `/locations/${this.props.location_name}/stay/room/${id}`
  }

  detailLinkDetails(id) {
    return {pathname: this.detailUrl(id), query: this.props.query}
  }

  render() {

    const roomRow = this.props.rooms.map((room) => {
      return (
        <tr key={room.id}>
          <td><Link key={room.id} to={this.detailLinkDetails(room.rid)} target={(this.props.drft ? "_blank" : "")}>{room.name}</Link></td>
          {room.availabilities.map(function(availability) {
            return <td key={availability.date} className={(availability.quantity > 0 ? "success" : "")}>{availability.quantity}</td>
          })}
        </tr>
      )
    })

    const dateColumn = this.props.rooms[0].availabilities.map((availability) => {
      return (
        <th key={availability.date}>{moment(availability.date).format('MMM DD')}</th>
      )
    })

    return (
      <div className="availability-area">
        <Table className="table-responsive availabilities-table">
          <thead>
            <tr>
              <th>Room Name</th>
              {dateColumn}
            </tr>
          </thead>
          <tbody>
            {roomRow}
          </tbody>
        </Table>
      </div>
    )
  }
}
