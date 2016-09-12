import React, {PropTypes} from 'react'

export default class DateRangeSelector extends React.Component {
  static propTypes = {
    onChange: PropTypes.func.isRequired
  }

  onDatesChanged() {
    this.props.onChange(this.refs.arrive.value, this.refs.depart.value)
  }

  render() {
    return (
      <div className="row">
        <div className="col-sm-2">Dates</div>
        <div className="col-sm-3">
					<input onChange={this.onDatesChanged.bind(this)} className="form-control" ref="arrive" type="text" placeholder="Arrive" autoComplete="off"/>
				</div>
				<div className="col-sm-3">
					<input className="form-control" ref="depart" type="text" placeholder="Depart" autoComplete="off"/>
				</div>
			</div>
    )
  }
}
