import React, {PropTypes} from 'react'
import moment from 'moment'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'

export default class BookingForm extends React.Component {
  static propTypes = {
    query: PropTypes.object.isRequired,
    room: PropTypes.object.isRequired,
    datesAvailable: PropTypes.bool.isRequired,
    onFilterChange: PropTypes.func.isRequired
  }

  onDateRangeChange(dates) {
    this.props.onFilterChange({dates: dates})
  }

  render() {
    const room = this.props.room
    const isDetail = true

    return (
      <div className="room-summary-panel">
        <DateRangeSelector onChange={this.onDateRangeChange.bind(this)} detail={isDetail} query={this.props.query} {...this.props.query} />
        {this.props.datesAvailable ?
          <div className="alert alert-success">These dates are available</div>
          :
          <div className="alert alert-warning">These dates are not available</div>
        }
        <p>${room.defaultRate} * {moment(this.props.query.depart).diff(moment(this.props.query.arrive), 'days')} nights<span className="pull-right">${room.defaultRate * moment(this.props.query.depart).diff(moment(this.props.query.arrive), 'days')}</span></p>
        <hr></hr>
        <p>SF Hotel Taxes <span className="pull-right">$</span></p>
        <hr></hr>
        <p><b>Total<span className="pull-right">$</span></b></p>
        <p>*Tell us a little about the purpose of your trip</p>
        <textarea className="form-control"></textarea>
        <p>Arrival time</p>
        <input className="form-control" type="time"></input>
        <button className="btn btn-primary btn-block">Request</button>
      </div>
    )

  }
}
