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

export class DrftMoney {
    constructor(props) {
      this.amount = props.amount
      this.currency = props.currency
    }

    getAmount() {
      return this.amount
    }

    getCurrency() {
      return 'drft'
    }
}

export class DrftLineItem extends LineItem {
  constructor(props) {
    super(props)
    this.nightRate = new DrftMoney ({
      amount: 1,
      currency: 'DRFT'
    })
    this.nights = props.nights
  }

  description() {
    return `Ɖ1 * ${this.nights} nights`
  }

  amount() {
    this.nightRate = new DrftMoney({
      amount: 1*this.nights,
      currency: 'DRFT'
    })
    return this.nightRate
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
    const nights = props.depart.diff(props.arrive, 'days')
    if (props.acceptDrftTheseDates && (props.drftBalance >= nights)) {
      this.drftItem = new DrftLineItem({
        id: 'base',
        nightRate: 1,
        nights: nights
      })
      this.feeItems = []
    }
    else {
      this.baseItem = new BaseLineItem({
        id: 'base',
        nightRate: props.nightRate,
        nights: nights
      })
      this.feeItems = this._buildFeeItems(props.fees || [], this.baseItem.amount())
      if (props.acceptDrftTheseDates && (props.drftBalance > 0) && (props.drftBalance < nights)) {
        this.desc = 'You have Ɖ'+`${props.drftBalance}`+', enough for '+`${props.drftBalance}`+ ' nights'
      } else if (props.hasFutureDrftCapacity && !props.acceptDrftTheseDates) {
        this.desc = 'This room accepts Ɖ, but not for these days'
      }
    }
  }

  lineItems() {
    return [
      this.baseItem || this.drftItem,
      ...this.feeItems
    ]
  }

  totalAmount() {
    return this._sumAmounts(this.lineItems())
  }

  drftDescription() {
    return this.desc
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
