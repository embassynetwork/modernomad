import React, {PropTypes} from 'react'

export default class AvailabilityForm extends React.Component {
  static propTypes = {
    onCancel: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired
  }

  submit(event) {
    const values = {
      start_date: this.refs.start_date.value,
      quantity: parseInt(this.refs.quantity.value) || 0
    }
    event.preventDefault()
    this.props.onSubmit(values);
  }

  render() {
    if (this.props.loading) {
      return (<div>loading...</div>);
    }
    let inputStyles = {display: "block", width: "100%"}
    return (
      <div className="well">
        <form className="form-inline" onSubmit={this.submit.bind(this)}>
          <div className="row">
            <div className="form-group col-xs-8">
              <label htmlFor="date" className="control-label" style={{display: 'block'}}>Start date</label>
              <input name="start_date" type="date" className="form-control" ref="start_date" required={true} style={inputStyles} />
            </div>
            <div className="form-group col-xs-4">
              <label htmlFor="quantity" className="control-label" style={{display: 'block'}}>Availability</label>
              <input name="quantity" type="number" className="form-control" min="0" max="100" ref="quantity" required={true} style={inputStyles} />
            </div>
          </div>
          <div>
            <a className="btn btn-default" onClick={this.props.onCancel}>Cancel</a>
            <button className="btn btn-primary pull-right">Submit</button>
          </div>
        </form>
      </div>
    );
  }
}
