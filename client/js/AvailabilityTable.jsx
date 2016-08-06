import React, {PropTypes} from 'react'
var moment = require('moment');

export default class AvailabilityTable extends React.Component {
  static propTypes = {
    availabilities: PropTypes.arrayOf({
      id: PropTypes.number.isRequired,
      start: PropTypes.string,
      quantity: PropTypes.number.isRequired
    }).isRequired
  }

  formatDate(date) {
    if (date) {
      const momentDate = moment(date);
      const formatString = (momentDate.year() == moment().year()) ? "Mo MMM" : "Mo MMM, Y"
      return momentDate.format(formatString)
    } else {
      return "now";
    }
  }

  render() {
    const availabilities = this.props.availabilities;

    const rows = availabilities.map((availiability) => {
      const className = (availiability.id == availabilities[0].id) ? 'success current' : ''
      const desc = `${availiability.quantity} booking${availiability.quantity == 1 ? '' : 's'}`
      return (
        <tr key={availiability.id} className={className}>
          <td>{this.formatDate(availiability.start)}</td>
          <td>{desc}</td>
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
