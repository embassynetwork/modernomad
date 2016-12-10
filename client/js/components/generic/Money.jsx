import React from 'react'
import ReactMoneyComponent from 'react-money-component';

export default function Money(props) {
  const money = props.money
  console.log(money.getCurrency())
  if (money.getCurrency() == 'drft') {
    return <span>Ɖ{money.getAmount()}</span>
  }
  else {
    return <ReactMoneyComponent cents={money.getAmount()} currency={money.getCurrency()} />
  }
}
