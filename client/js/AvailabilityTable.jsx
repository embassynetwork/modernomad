import React, {PropTypes} from 'react'
import AvailabilityForm from './AvailabilityForm'
import CurrentAvailability from './CurrentAvailability'
var moment = require('moment');

const availabilitySchema = PropTypes.shape({
  id: PropTypes.number.isRequired,
  start: PropTypes.string,
  quantity: PropTypes.number.isRequired
})

export default class AvailabilityTable extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      showForm: false
    }
  }

  static propTypes = {
    currentAvailability: availabilitySchema,
    upcomingAvailabilities: PropTypes.arrayOf(availabilitySchema).isRequired
  }

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

  openForm() {
    this.setState({showForm: true})
  }

  closeForm() {
    this.setState({showForm: false})
  }

  onFormSubmit(values) {
    console.log("values received from form", values)
  }

  renderForm() {
    if (this.state.showForm) {
      return <AvailabilityForm onCancel={this.closeForm.bind(this)} onSubmit={this.onFormSubmit.bind(this)} />
    } else {
      return <button className="btn btn-default" onClick={this.openForm.bind(this)}>Schedule a change</button>
    }
  }

  render() {
    const availabilities = this.props.upcomingAvailabilities;

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

    return <div>
      <CurrentAvailability availability={this.props.currentAvailability} />
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
      {this.renderForm()}
    </div>;
  }
}
