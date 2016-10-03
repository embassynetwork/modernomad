import React, {PropTypes} from 'react'
import DatePicker from 'react-datepicker'
import moment from 'moment'

function momentUnlessNull(dateString, parseFormat = null) {
  return dateString ? moment(dateString, parseFormat) : null
}

export default class DateRangeSelector extends React.Component {
  static propTypes = {
    onChange: PropTypes.func.isRequired
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
        if (this.state.depart < minDepartValue) {
          newState.depart = minDepartValue
        }
      }

      const combinedState = {...this.state, ...newState}

      this.setState(newState)

      if (combinedState.arrive && combinedState.depart) {
        this.props.onChange(combinedState)
      }
    }
  }

  minDepart(currentArrive) {
    const bestArrive = currentArrive || this.state.arrive
    const arrival = bestArrive || moment()
    return arrival.clone().add(1, 'days')
  }

  render() {
    return (
      <div className="row">
        <div className="col-md-2 col-sm-4"><h5>Dates</h5></div>
        <div className={(this.props.detail ? "col-md-5" : "col-md-2 col-sm-4")}>
          <DatePicker placeholderText="Arrive" className="form-control" selected={this.state.arrive} onChange={this.changeHandler('arrive')} minDate={moment()} />
				</div>
				<div className={(this.props.detail ? "col-md-5" : "col-md-2 col-sm-4")}>
          <DatePicker placeholderText="Depart" className="form-control" selected={this.state.depart} onChange={this.changeHandler('depart')} minDate={this.minDepart()} />
				</div>
			</div>
    )
  }
}
