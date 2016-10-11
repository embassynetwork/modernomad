import React, {PropTypes} from 'react'
import DatePicker from 'react-datepicker'
import moment from 'moment'
import _ from 'lodash'

function momentUnlessNull(dateString, parseFormat = null) {
  return dateString ? moment(dateString, parseFormat) : null
}

export default class DateRangeSelector extends React.Component {
  static propTypes = {
    onChange: PropTypes.func.isRequired,
    maxLength: PropTypes.number,
    inputClass: PropTypes.string
  }

  constructor(props) {
    super(props)
    const parseFormat = 'MM/DD/YYYY'
    this.state = {arrive: momentUnlessNull(props.arrive, parseFormat), depart: momentUnlessNull(props.depart, parseFormat)}
  }

  changeHandler(key) {
    return (value) => {
      let newState = {}
      newState[key] = value

      if (newState.arrive && this.state.depart) {
        const minDepartValue = this.minDepart(newState.arrive)
        const maxDepartValue = this.maxDepart(newState.arrive)

        if (this.state.depart < minDepartValue) newState.depart = minDepartValue
        if (this.state.depart > maxDepartValue) newState.depart = maxDepartValue
      }

      const combinedState = {...this.state, ...newState}

      this.setState(newState)

      if (combinedState.arrive && combinedState.depart) {
        this.props.onChange(combinedState)
      }
    }
  }

  minDepart(currentArrive) {
    const bestArrive = currentArrive || this.state.arrive || moment()
    return bestArrive.clone().add(1, 'days')
  }

  maxDepart(currentArrive) {
    if (!this.props.maxLength) return null

    const bestArrive = currentArrive || this.state.arrive || moment()
    return bestArrive.clone().add(this.props.maxLength, 'days')
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
            minDate={moment()} />
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
            maxDate={this.maxDepart()}
            />
        </div>
      </div>
    )
  }
}

// minDate={this.minDepart()}
// maxDate={this.maxDepart()}
