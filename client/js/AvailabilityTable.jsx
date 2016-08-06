import React from 'react'
var moment = require('moment');

export default class AvailabilityTable extends React.Component {
  formatDate(date) {
    if (date) {
      const formatString = (date.year() == moment().year()) ? "Mo MMM" : "Mo MMM, Y"
      return date.format(formatString)
    } else {
      return "now";
    }
  }

  render() {
    const availabilities = [
      {id: 1, start: null, quantity: 1},
      {id: 2, start: moment("2016-02-03"), quantity: 3},
      {id: 3, start: moment("2016-03-01"), quantity: 0},
      {id: 4, start: moment("2018-12-25"), quantity: 20}
    ]

    const rows = availabilities.map((availiability) => {
      const className = (availiability.id == availabilities[0].id) ? 'success current' : ''
      return (
        <tr key={availiability.id} className={className}>
          <td>{this.formatDate(availiability.start)}</td>
          <td>{availiability.quantity} booking</td>
          <td></td>
        </tr>
      )
    });

    return <div>
      <table className="table table-striped availabilities-table">
        <thead>
          <tr>
            <th>Starting</th>
            <th>Availability for...</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
      <button className="btn btn-default">Add availability</button>
    </div>;
  }
}
