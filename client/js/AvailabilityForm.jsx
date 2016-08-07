import React from 'react'

export default class AvailabilityForm extends React.Component {
  render() {
    return (
      <div className="well">
        <form className="form-inline">
          <div className="row">
            <div className="form-group col-xs-8">
              <label for="inputEmail3" className="control-label">Start date</label>
              <input type="date" className="form-control" id="inputEmail3" placeholder="date" />
            </div>
            <div className="form-group col-xs-4">
              <label for="inputEmail3" className="control-label">Availability</label>
              <input type="number" className="form-control" id="inputEmail3" min="0" max="100" />
            </div>
          </div>
          <button className="btn btn-primary">Submit</button>
        </form>
      </div>
    );
  }
}
