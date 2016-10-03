import React, {PropTypes} from 'react'
var moment = require('moment');

export default class QuantityIndicator extends React.Component {
  static propTypes = {
    quantity: PropTypes.number.isRequired
  }

  render() {
    const colour = (this.props.quantity > 0 ? "#3c763d" : "red");
    const styles = {
      backgroundColor: "#DDDDDD",
      color: colour,
      border: `1px solid ${colour}`,
      display: "inline-block",
      padding: "0 6px",
      borderRadius: "4px"
    }
    return <span style={styles}>{this.props.quantity}</span>
  }
}
