import React, {PropTypes} from 'react'

export default class ScheduledBackingsTable extends React.Component {
  // static propTypes = {
  //   backings: PropTypes.array.isRequired
  // }

  constructor(props) {
    super(props)
  }

  renderBackings() {
    return this.props.backings.map((backing) => {
      return <div key={backing.node.id}>{backing.node.resourceId}</div>
    })
  }

  render() {
    console.log('yes',this.props.backings)
    return (
      <div>{this.renderBackings()}</div>
    )
  }
}
