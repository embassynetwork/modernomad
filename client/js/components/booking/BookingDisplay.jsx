import React from 'react'
import _ from 'lodash'
import { Booking } from '../../models/Booking'
import MoneyDisplay from '../generic/Money';

function LineItemDisplay(props) {
  const lineItem = props.lineItem

  return (
    <p>
      {lineItem.description()}
      <span className="pull-right">
        <MoneyDisplay money={lineItem.amount()} />
      </span>
    </p>
  )
}

export default function BookingDisplay(props) {
  const booking = props.booking
  const lineItems = booking.lineItems()

  var lines = []

  if (lineItems.length > 0) {
    lines = _.map(lineItems, (lineItem) => {
      return <LineItemDisplay key={lineItem.id} lineItem={lineItem} />
    })
  } else {
    return null
  }

  return (
    <div>
      {lines}
      <p>SF Hotel Taxes <span className="pull-right">$</span></p>
      <hr></hr>
      <p><b>Total<span className="pull-right">$</span></b></p>
    </div>
  )
}
