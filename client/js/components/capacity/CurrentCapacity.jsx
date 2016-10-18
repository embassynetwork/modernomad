import React, {PropTypes} from 'react'
import QuantityIndicator from './QuantityIndicator'
var moment = require('moment');

export default class CurrentCapacity extends React.Component {
  static propTypes = {
    capacity: PropTypes.shape({
      quantity: PropTypes.number.isRequired
    })
  }

  quantity() {
    return this.props.capacity ? this.props.capacity.quantity : 0
  }

  renderQuantityIndicator(quantity) {
    return <QuantityIndicator quantity={quantity} />
  }

  renderDescription() {
    const quantity = this.quantity();

    return (<p>
      Currently accepts {this.renderQuantityIndicator(quantity)} bookings
      at a time
    </p>)
  }

  render() {
    return (
      <div style={{fontSize: "150%"}}>
        <h3>Capacity</h3>
        {this.renderDescription()}
      </div>
    )
  }
}
