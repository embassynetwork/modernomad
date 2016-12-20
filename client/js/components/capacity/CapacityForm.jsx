import React, {PropTypes} from 'react'
import DatePicker from '../generic/DatePicker'

export default class CapacityForm extends React.Component {
  static propTypes = {
    onCancel: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired
  }

  submit(event) {
    const values = {
	  start_date: this.refs.start_date.value(),
      quantity: parseInt(this.refs.quantity.value) || 0,
      accept_drft: this.refs.accept_drft.checked
    }
    event.preventDefault()
    this.props.onSubmit(values);
  }

  render() {
    let inputStyles = {display: "block", width: "100%"}
    return (
      <div className="well">
        <form className="form-inline" onSubmit={this.submit.bind(this)}>
          <div className="row">
            <div className="form-group col-xs-8">
              <label htmlFor="date" className="control-label" style={{display: 'block'}}>Start date</label>
              <DatePicker name="start_date" className="form-control" ref="start_date" required={true} style={inputStyles} disabled={this.props.loading} />
            </div>
            <div className="form-group col-xs-2">
              <label htmlFor="quantity" className="control-label" style={{display: 'block'}}>Capacity</label>
              <input name="quantity" type="number" className="form-control" min="0" max="100" ref="quantity" required={true} style={inputStyles} disabled={this.props.loading} />
            </div>
            <div className="form-group col-xs-2">
              <label htmlFor="accept_drft" className="control-label" style={{display: 'block'}}>DRFT?</label>
              <input name="accept_drft" type="checkbox" className="form-control" ref="accept_drft" style={inputStyles} disabled={this.props.loading} />
            </div>
          </div>
          <div>
            <a className="btn btn-default" onClick={this.props.onCancel}>Cancel</a>
            <button className="btn btn-primary pull-right" disabled={this.props.loading}>Submit</button>
          </div>
        </form>
      </div>
    );
  }
}
