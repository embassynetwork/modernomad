import Money from 'js-money'

function roundToTwo(num) {
  return +(Math.round(num + "e+2")  + "e-2");
}

export class LineItem {
  constructor(props) {
    this.id = props.id
  }

  description() {
    return 'unknown'
  }

  amount() {
    return Money.fromDecimal(0.0, 'USD')
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


export class FeeLineItem extends LineItem {
  constructor(props) {
    super(props)
    this.fee = props.fee
    this.previousTotal = props.previousTotal
    this.id = props.fee.id
  }

  description() {
    return `${this.fee.description} (${this.fee.percentage*100}%)`
  }

  amount() {
    return this.previousTotal.multiply(this.fee.percentage)
  }
}


export class Booking {
  constructor(props) {
    this.baseItem = new BaseLineItem({
      id: 'base',
      nightRate: props.nightRate,
      nights: props.depart.diff(props.arrive, 'days')
    })
    this.feeItems = this._buildFeeItems(props.fees || [], this.baseItem.amount())
  }

  lineItems() {
    return [
      this.baseItem,
      ...this.feeItems
    ]
  }

  totalAmount() {
    return this._sumAmounts(this.lineItems())
  }

  _sumAmounts(lineItems) {
    var result = null
    lineItems.forEach((item) => {
      const itemAmount = item.amount()
      result = result ? result.add(itemAmount) : itemAmount
    })
    return result
  }

  _buildFeeItems(fees, baseAmount) {
    var runningTotal = baseAmount

    return _.map(fees, (fee) => {
      var item = new FeeLineItem({fee: fee, previousTotal: runningTotal})
      runningTotal = runningTotal.add(item.amount())
      return item
    })
  }
}
