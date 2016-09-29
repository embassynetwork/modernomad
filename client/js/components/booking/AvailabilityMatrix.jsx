import React, {PropTypes} from 'react'
import { Table } from 'react-bootstrap'
import { Link } from 'react-router'
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
    return `/locations/${this.props.routeParams.location}/stay/room/${id}`
  }

  detailLinkDetails(id) {
    return {pathname: this.detailUrl(id), query: this.props.query}
  }

  render() {

    const roomRow = this.props.rooms.map((room) => {
      return (
        <tr key={room.id}>
          <td><Link key={room.id} to={this.detailLinkDetails(room.rid)}>{room.name}</Link></td>
          {room.bookabilities.map(function(bookability) {
            return <td key={bookability.date} className={(bookability.quantity ? "success" : "")}>{bookability.quantity}</td>
          })}
        </tr>
      )
    })

    const dateColumn = this.props.rooms[0].bookabilities.map((bookability) => {
      return (
        <th key={bookability.date}>{moment(bookability.date).format('MMM DD')}</th>
      )
    })

    return (
      <div className="availability-area">
        <Table className="panel table-responsive availabilities-table">
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
