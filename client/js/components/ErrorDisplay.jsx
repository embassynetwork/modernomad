import React, {PropTypes} from 'react'

export default class ErrorDisplay extends React.Component {
  static propTypes = {
    errors: PropTypes.object.isRequired
  }

  render() {
    return (
      <div>
        some errors
      </div>
    )
  }
}
