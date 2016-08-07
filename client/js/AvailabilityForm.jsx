import React, {PropTypes} from 'react'

export default class AvailabilityForm extends React.Component {
  static propTypes = {
    onCancel: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired
  }

  submit(event) {
    const values = {
      date: this.refs.date.value,
      quantity: parseInt(this.refs.quantity.value) || 0
    }
    event.preventDefault()
    this.props.onSubmit(values);
  }

  render() {
    return (
      <div className="well">
        <form className="form-inline" onSubmit={this.submit.bind(this)}>
          <div className="row">
            <div className="form-group col-xs-8">
              <label htmlFor="date" className="control-label">Start date</label>
              <input name="date" type="date" className="form-control" ref="date" required={true} />
            </div>
            <div className="form-group col-xs-4">
              <label htmlFor="quantity" className="control-label">Availability</label>
              <input name="quantity" type="number" className="form-control" min="0" max="100" ref="quantity" required={true} />
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
