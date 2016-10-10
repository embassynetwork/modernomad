import React, {PropTypes} from 'react'
import moment from 'moment'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'
import { Link } from 'react-router'
import DjangoCSRFInput from '../generic/DjangoCSRFInput'


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

  renderCost() {
    const depart = moment(this.props.query.depart, parseFormat)
    const arrive = moment(this.props.query.arrive, parseFormat)
    const parseFormat = 'MM/DD/YYYY'

    if (depart && arrive) {
      const nightRate = this.props.room.defaultRate
      const nights = depart.diff(arrive, 'days')
      const totalCost = nightRate * nights
      return <p>${nightRate} * {nights} nights<span className="pull-right">${totalCost}</span></p>
    } else {
      return null;
    }
  }

  indexLinkDetails() {
    if (this.props.query.arrive) {
      return {
        pathname: `/locations/${this.props.routeParams.location}/stay/`,
        query: this.props.query
      }
    } else {
      return {
        pathname: `/locations/${this.props.routeParams.location}/stay/`
      }
    }
  }

  render() {
    const room = this.props.room
    const isDetail = true
    const submitUrl = `/locations/${this.props.routeParams.location}/booking/submit`

    return (
      <form className="booking-request-form" method="POST" action={submitUrl}>
        <DjangoCSRFInput />
        <input type="hidden" name="resource" value={room.rid} />
        <div className="row nightly-price">
          <h3 className="col-xs-8">${this.props.room.defaultRate}</h3>
          <div className="col-xs-4"><h5 className="pull-right">Per Night</h5></div>
        </div>
        <div className="date-row">
          <DateRangeSelector onChange={this.onDateRangeChange.bind(this)} detail={isDetail} query={this.props.query} {...this.props.query} />
        </div>
        {this.props.datesAvailable || !this.props.query.arrive ?
          <div>
            {this.props.datesAvailable ?
              <div>
                {this.renderCost()}
                <p>SF Hotel Taxes <span className="pull-right">$</span></p>
                <hr></hr>
                <p><b>Total<span className="pull-right">$</span></b></p>
                <p>*Tell us a little about the purpose of your trip</p>
                <textarea className="form-control" name="purpose" required="true" />
                <p>Arrival time</p>
                <input className="form-control" name="arrival_time" />
                <p>Comments</p>
                <textarea className="form-control" name="comments" />
              </div>
              :
              <div></div>
            }
            <button className="btn btn-primary btn-block btn-brand" id="submit-booking-request">Request to Book</button>
            <p className="text-center">Your credit card won't be charged</p>

          </div>
          :
          <div>
            <p className="text-center">Those dates are not available</p>
            <Link className="btn btn-default btn-block" to={this.indexLinkDetails()}>View other rooms</Link>
          </div>
        }
      </form>
    )

  }
}
