import React, {PropTypes} from 'react'
import DatePicker from 'react-datepicker'
import moment from 'moment'
import _ from 'lodash'
import DATEFORMAT from './constants'

function momentUnlessNull(dateString, parseFormat = null) {

  let date = dateString ? moment(dateString, parseFormat) : null
  if (date != null && !date.isValid()) {
    // if a string is supplied, make sure it's always valid
    return moment()
  }
  return date
}

export default class DateRangeSelector extends React.Component {
  static propTypes = {
    onChange: PropTypes.func.isRequired,
    maxLength: PropTypes.number,
    inputClass: PropTypes.string
  }

  constructor(props) {
    super(props)

    const arrive = momentUnlessNull(props.arrive, DATEFORMAT)
    const depart = momentUnlessNull(props.depart, DATEFORMAT)
    const dates = {arrive: arrive, depart: depart}
    this.state = this.constrainDateRangeByStart(dates, props.maxLength)
    if (dates.depart != depart && props.onChange) {
      setTimeout(() => {
        props.onChange(dates)
      }, 0)
    }
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.maxLength != nextProps.maxLength) {
      const currentDates = this.currentDates()
      const newDates = this.constrainDateRangeByStart(currentDates, nextProps.maxLength)
      if (newDates.arrive != currentDates.arrive || newDates.depart != currentDates.depart) {
        this.setState(newDates)
        this.props.onChange(newDates)
      }
    }
  }

  currentDates() {
    return {arrive: this.state.arrive, depart: this.state.depart}
  }

  changeHandler(key) {
    return (value) => {
      let newState = {}
      newState[key] = value

      newState.depart = this.constrainedDepartDate(
        newState.arrive,
        newState.depart || this.state.depart,
        this.props.maxLength
      )

      const combinedState = {...this.state, ...newState}

      this.setState(newState)
      if (combinedState.arrive && combinedState.depart) {
        this.props.onChange(combinedState)
      }
    }
  }

  constrainDateRangeByStart(dates, maxLength) {
    const newArrive = this.constrainArriveDate(dates.arrive)
    const newDepart = this.constrainedDepartDate(newArrive, dates.depart, maxLength)
    return {arrive: newArrive, depart: newDepart}
  }

  constrainArriveDate(arrive) {
    if (arrive) {
      const today = moment()
      if (arrive < today) {
        return today
      }
    }
    return arrive
  }

  constrainedDepartDate(newArrive, existingDepart, maxLength) {
    if (newArrive) {
      const minDepartValue = this.minDepart(newArrive)
      const maxDepartValue = this.maxDepart(newArrive, maxLength)

      return this.constrainDate(existingDepart, minDepartValue, maxDepartValue)
    } else {
      return existingDepart
    }
  }

  constrainDate(value, min, max) {
    if (value) {
      if (min && value < min) value = min
      if (max && value > max) value = max
    }
    return value
  }

  minDepart(currentArrive) {
    const bestArrive = currentArrive || this.state.arrive || moment()
    return bestArrive.clone().add(1, 'days')
  }

  maxDepart(currentArrive, maxLength) {
    if (!maxLength) return null

    const bestArrive = currentArrive || this.state.arrive || moment()
    return bestArrive.clone().add(maxLength, 'days')
  }

  render() {
    const controlClasses = _.join(["form-control", this.props.inputClass], ' ')

    return (
      <div className="row">
        <div className={(this.props.detail ? "col-sm-2" : "col-md-2 col-sm-4")}><h4 className={(this.props.detail ? "detail-size" : "index-size")}>Dates</h4></div>
        <div className={(this.props.detail ? "col-sm-5" : "col-md-2 col-sm-4")}>
          <DatePicker name="arrive"
            placeholderText="Arrive"
            selectsStart
            className={controlClasses}
            selected={this.state.arrive}
            startDate={this.state.arrive}
            endDate={this.state.depart}
            onChange={this.changeHandler('arrive')}
            minDate={moment()}
            autoComplete="off" />
        </div>
        <div className={(this.props.detail ? "col-sm-5" : "col-md-2 col-sm-4")}>
          <DatePicker name="depart"
            placeholderText="Depart"
            selectsEnd
            className={controlClasses}
            selected={this.state.depart}
            startDate={this.state.arrive}
            endDate={this.state.depart}
            onChange={this.changeHandler('depart')}
            minDate={this.minDepart()}
            maxDate={this.maxDepart(null, this.props.maxLength)}
            autoComplete="off"
            />
        </div>
      </div>
    )
  }
}
