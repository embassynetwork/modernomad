import React from 'react'
var moment = require('moment');

export default class AvailabilityTable extends React.Component {
  formatDate(date) {
    if (date) {
      const momentDate = moment(date);
      if (momentDate > moment().endOf("day")) {
        const formatString = (momentDate.year() == moment().year()) ? "Mo MMM" : "Mo MMM, Y"
        return momentDate.format(formatString)
      }
    }
    return "now";
  }

  render() {
    const availabilities = this.props.availabilities;

    const rows = availabilities.map((availiability) => {
      const desc = `${availiability.quantity}`
      return (
        <tr key={availiability.id}>
          <td>{this.formatDate(availiability.start)}</td>
          <td><span className="text-success" style={{backgroundColor: "#DDDDDD", border: "1px solid #3c763d", display: "inline-block", padding: "0 6px", borderRadius: "4px"}}>{desc}</span></td>
          <td><a><i className="fa fa-trash pull-right" /></a></td>
        </tr>
      )
    });

    return (
      <div className="panel panel-default">
        <div className="panel-heading">
          <h4>Upcoming changes</h4>
        </div>
        <table className="table table-striped availabilities-table">
          <thead>
            <tr>
              <th>On</th>
              <th>Availability changes to</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    );
  }
}
