import React, {PropTypes} from 'react'
import AvailabilityForm from './AvailabilityForm'
var moment = require('moment');

export default class AvailabilityTable extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      showForm: false
    }
  }

  static propTypes = {
    availabilities: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.number.isRequired,
      start: PropTypes.string,
      quantity: PropTypes.number.isRequired
    })).isRequired
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

  openForm() {
    this.setState({showForm: true})
  }

  closeForm() {
    this.setState({showForm: false})
  }

  renderForm() {
    if (this.state.showForm) {
      return <AvailabilityForm onCancel={this.closeForm.bind(this)} />
    } else {
      return <button className="btn btn-default" onClick={this.openForm.bind(this)}>Add availability</button>
    }
  }

  render() {
    const availabilities = this.props.availabilities;

    const rows = availabilities.map((availiability) => {
      const currentRow = availiability.id == availabilities[0].id;
      const className = currentRow ? 'success current' : ''
      const desc = `${availiability.quantity} booking${availiability.quantity == 1 ? '' : 's'}`
      return (
        <tr key={availiability.id} className={className}>
          <td>{this.formatDate(availiability.start)}</td>
          <td>{desc}</td>
          <td>{currentRow ? null : <a><i className="fa fa-trash pull-right" /></a>}</td>
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
      {this.renderForm()}
    </div>;
  }
}
