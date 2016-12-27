import React, {PropTypes} from 'react'
import moment from 'moment'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'
import { Link } from 'react-router'
import { Panel, FormGroup, ControlLabel, FormControl, OverlayTrigger, Tooltip } from 'react-bootstrap';
import DjangoCSRFInput from '../generic/DjangoCSRFInput'
import BookingDisplay from './BookingDisplay'
import { Booking } from '../../models/Booking'

export default class BookingForm extends React.Component {
  static propTypes = {
    query: PropTypes.object.isRequired,
    room: PropTypes.object.isRequired,
    datesAvailable: PropTypes.bool.isRequired,
    onFilterChange: PropTypes.func.isRequired
  }

  constructor(props) {
    super(props)
    this.state = {open: false, showValidation: false}
  }

  onDateRangeChange(dates) {
    this.props.onFilterChange({dates: dates})
  }

  renderCost() {
    const parseFormat = 'MM/DD/YYYY'
    const depart = moment(this.props.query.depart, parseFormat)
    const arrive = moment(this.props.query.arrive, parseFormat)
    const acceptDrftTheseDates = this.props.room.acceptDrftTheseDates
    const drftBalance = this.props.route.drftBalance

    if (depart && arrive) {
      const booking = new Booking({
        nightRate: this.props.room.defaultRate,
        arrive: arrive,
        depart: depart,
        fees: this.props.networkLocation.fees,
        drftBalance: drftBalance,
        acceptDrftTheseDates: acceptDrftTheseDates
      })
      return <BookingDisplay booking={booking} />
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

  handlePanel() {
     this.setState({ open: !this.state.open })
  }

  checkValid(event) {
    if (!this.valid()) {
      event.preventDefault();
      this.setState({showValidation: true})
    }
  }

  valid() {
    return !!this.state.purpose
  }

  validationState() {
    if (this.state.showValidation) {
      return this.valid() ? 'success' : 'error'
    }
  }

  changePurpose(event) {
    this.setState({purpose: event.target.value})
  }


  render() {
    const room = this.props.room
    const submitUrl = `/locations/${this.props.routeParams.location}/booking/submit`
    const drftTooltip = (
      <Tooltip id="tooltip">Ɖ or DRFT is a housing currency currently in beta mode.</Tooltip>
    );

    if (!this.props.networkLocation) return null;

    return (
      <form className="booking-request-form" method="POST" action={submitUrl} onSubmit={this.checkValid.bind(this)}>
        <DjangoCSRFInput />
        <input type="hidden" name="resource" value={room.rid} />
        <div className="row nightly-price">
          <h3 className="col-xs-8">${this.props.room.defaultRate}
            {this.props.room.acceptDrftTheseDates?
              <span><span className="h5"> or </span>Ɖ1
                <OverlayTrigger placement="top" overlay={drftTooltip}>
                  <span className="fa fa-info-circle drft-info"></span>
                </OverlayTrigger>
              </span>
              :
              <span></span>
            }
          </h3>
          <div className="col-xs-4"><h5 className="pull-right">Per Night</h5></div>
        </div>
        <div className="date-row">
          <DateRangeSelector
            onChange={this.onDateRangeChange.bind(this)}
            maxLength={this.props.networkLocation.maxBookingDays}
            detail={true} {...this.props.query} />
        </div>
        {this.props.datesAvailable || !this.props.query.arrive ?
          <div>
            {this.props.datesAvailable ?
              <div>
                {this.renderCost()}

                <FormGroup validationState={this.validationState()} controlId="formControlsTextarea">
                  <p>*Tell us a little about the purpose of your trip</p>
                  {this.validationState() == 'error' && <ControlLabel>You must write a purpose for your stay</ControlLabel>}
                  <FormControl componentClass="textarea" name="purpose" onChange={this.changePurpose.bind(this)} />
                </FormGroup>

                <p>
                  <a className="btn-link" onClick={this.handlePanel.bind(this)}>
                    <span className={(this.state.open ? "fa fa-chevron-down" : "fa fa-chevron-right")}></span> Optional fields
                  </a>
                </p>
                <Panel collapsible expanded={this.state.open} className="optional-fields">
                  <p>Arrival time</p>
                  <input className="form-control" name="arrival_time" />
                  <p>Comments</p>
                  <textarea className="form-control" name="comments" />
                </Panel>
              </div>
              :
              <div></div>
            }
            <button className="btn btn-primary btn-block btn-brand" id="submit-booking-request">Request to Book</button>

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
