import React, {PropTypes} from 'react'
import moment from 'moment'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'

export default class RoomDetail extends React.Component {
  static propTypes = {
    room: PropTypes.object.isRequired,
    onFilterChange: PropTypes.func.isRequired
  }

  onDateRangeChange(dates) {
    this.props.onFilterChange({dates: dates})
  }

  hasDateQuery() {
    return this.props.query.arrive
  }

  bookableRoom() {
    if (this.hasDateQuery()) {
      console.log(_.find(this.props.room.bookabilities, {quantity: 0}))
      return _.find(this.props.room.bookabilities, {quantity: 0})
    } else {
      return this.props.room
    }
  }

  render() {
    const room = this.props.room
    const isDetail = true

    return (
      <div className="container">
        <h1>{room.name}</h1>
        <p>{room.summary}</p>
        <div className="row">
          <div className="col-sm-8">
            <img className="room-image" src={"/media/"+room.image} />
            {/*room.img && <ImageCarousel img={room.img} />*/}
          </div>
          <div className="col-sm-4 panel">
            <div className="room-summary-panel">
              <DateRangeSelector onChange={this.onDateRangeChange.bind(this)} detail={isDetail} query={this.props.query} {...this.props.query} />
              {this.bookableRoom() ?
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
          </div>
        </div>
      </div>
    )

  }
}
