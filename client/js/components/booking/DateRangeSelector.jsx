import React, {PropTypes} from 'react'
import DatePicker from 'react-datepicker'
import moment from 'moment'

function momentUnlessNull(dateString) {
  return dateString ? moment(dateString) : null
}

export default class DateRangeSelector extends React.Component {
  static propTypes = {
    onChange: PropTypes.func.isRequired
  }

  constructor(props) {
    super(props)
    this.state = {arrive: momentUnlessNull(props.arrive), depart: momentUnlessNull(props.depart)}
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
        <div className="col-sm-2">Dates</div>
        <div className="col-sm-3">
          <DatePicker className="form-control" selected={this.state.arrive} onChange={this.changeHandler('arrive')} minDate={moment()} />
				</div>
				<div className="col-sm-3">
          <DatePicker className="form-control" selected={this.state.depart} onChange={this.changeHandler('depart')} minDate={this.minDepart()} />
				</div>
			</div>
    )
  }
}
