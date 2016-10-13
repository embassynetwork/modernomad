import React from 'react'
import ReactMoneyComponent from 'react-money-component';

export default function Money(props) {
  const money = props.money
  return <ReactMoneyComponent cents={money.getAmount()} currency={money.getCurrency()} />
}
