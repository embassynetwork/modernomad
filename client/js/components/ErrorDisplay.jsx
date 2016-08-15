import React, {PropTypes} from 'react'
import {flatMap} from 'lodash'
import humanize from 'humanize-string'

export default class ErrorDisplay extends React.Component {
  static propTypes = {
    errors: PropTypes.object.isRequired
  }

  render() {
    const errors = flatMap(this.props.errors, (message, field_name) => {
      return <li>{humanize(field_name)}: {message}</li>
    })

    return (
      <div className="alert alert-danger">
        <ul className="error-list">
          {errors}
        </ul>
      </div>
    )
  }
}
