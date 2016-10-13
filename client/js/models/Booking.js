import Money from 'js-money'

function roundToTwo(num) {
  return +(Math.round(num + "e+2")  + "e-2");
}

export class LineItem {
  constructor(props) {
    this.id = props.id
  }
}

export class BaseLineItem extends LineItem {
  constructor(props) {
    super(props)
    this.nightRate = Money.fromDecimal(props.nightRate, 'USD')
    this.nights = props.nights
  }

  description() {
    return `$${this.nightRate} * ${this.nights} nights`
  }

  amount() {
    return this.nightRate.multiply(this.nights)
  }
}


export class Booking {
  constructor(props) {
    this.baseItem = new BaseLineItem({
      id: 'base',
      nightRate: props.nightRate,
      nights: props.depart.diff(props.arrive, 'days')
    })
  }

  lineItems() {
    return [
      this.baseItem
    ]
  }

  totalAmount() {
    this.baseItem.amount()
  }
}
