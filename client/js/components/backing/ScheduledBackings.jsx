import React, {PropTypes} from 'react'

export default class ScheduledBackings extends React.Component {
  // defines required arguments
  static propTypes = {
    backings: PropTypes.array.isRequired
  }

  render() {

    const {backings} = this.props
    
    const rows = backings.map((backing) => {
        return <div key={backing.toString()}>{backing}</div>
    })

    return (
      <div className="row">
        <div className="col-md-12">
            {rows}
        </div>
      </div>
    )
  }
}
