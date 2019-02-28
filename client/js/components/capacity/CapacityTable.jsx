import React, {PropTypes} from 'react'
import ReactCSSTransitionGroup from 'react-addons-css-transition-group'
var moment = require('moment');

export default class CapacityTable extends React.Component {
  static propTypes = {
    onDelete: PropTypes.func.isRequired
  }

  formatDate(date) {
    if (date) {
      const momentDate = moment(date);
      if (momentDate > moment().endOf("day")) {
        const formatString = (momentDate.year() == moment().year()) ? "Do MMM" : "Do MMM, Y"
        return momentDate.format(formatString)
      }
    }
    return "now";
  }

  formatDrft(bool) {
      if (bool == 'true') {
          return <i className="fa fa-check"></i>
      } else {
          return <i className="fa fa-close"></i>
      }
  }

  render() {
    const capacities = this.props.capacities;

    const rows = capacities.map((capacity) => {
      const desc = `${capacity.quantity}`
      const drft = `${capacity.accept_drft}`
      const onDelete = (event) => {
        event.preventDefault();
        this.props.onDelete(capacity.id);
      }
      return (
        <tr key={capacity.id}>
          <td>{this.formatDate(capacity.start_date)}</td>
          <td><span className="text-success" style={{backgroundColor: "#DDDDDD", border: "1px solid #3c763d", display: "inline-block", padding: "0 6px", borderRadius: "4px"}}>{desc}</span></td>
          <td>{this.formatDrft(drft)}</td>
          <td><a onClick={onDelete} href="#"><i className="fa fa-trash pull-right" /></a></td>
        </tr>
      )
    });

    return (
      <div className="panel panel-default">
        <div className="panel-heading">
          <h4>Upcoming changes</h4>
        </div>
        <table className="table table-striped capacities-table">
          <thead>
            <tr>
              <th>On</th>
              <th>Capacity changes to</th>
              <th>DRFT</th>
            </tr>
          </thead>
          <ReactCSSTransitionGroup component="tbody" transitionName="animrow" transitionEnterTimeout={1500} transitionLeave={false}>
            {rows}
          </ReactCSSTransitionGroup>
        </table>
      </div>
    );
  }
}
