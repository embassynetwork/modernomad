import React, {PropTypes} from 'react'
var moment = require('moment');

export default class ScheduledBackingsTable extends React.Component {
  static propTypes = {
    backings: PropTypes.array.isRequired
    }

  formatDate(date) {
    const momentDate = moment(date);
    const formatString = (momentDate.year() == moment().year()) ? "Do MMM" : "Do MMM, Y"
    return momentDate.format(formatString)
  }

  renderDetails(backing) {
    var backers = backing.users.edges.map((u) => {
        return (
            <a key={u.node.id} href={`/people/${u.node.username}`}>
                {`${u.node.firstName} ${u.node.lastName}, `} 
            </a>
        )
    })

    return (
        <div key={backing.id}>
            <strong>Scheduled backing changes: </strong>
            {backers} on {this.formatDate(backing.start)}
        </div>
    ) 
  }

  renderBackings() {
    const {backings} = this.props

    return backings.map((backing) => {
        return this.renderDetails(backing)
    })

  }

  render() {
    const html = this.props.backings.length > 0
    ? this.renderBackings()
    : "No scheduled backing changes"
    return <div>{html}</div>
  }
}
