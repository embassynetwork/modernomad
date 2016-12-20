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
  const drftDescription = booking.drftDescription()


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
      <hr></hr>
      <p>
        <b>
          Total
          <span className="pull-right">
            <MoneyDisplay money={booking.totalAmount()} />
          </span>
        </b>
      </p>
      <p className="text-center">
        <em>{drftDescription}</em>
      </p>
    </div>
  )
}
