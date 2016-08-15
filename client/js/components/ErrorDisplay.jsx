import React, {PropTypes} from 'react'
import {flatMap} from 'lodash'
import humanize from 'humanize-string'

export default class ErrorDisplay extends React.Component {
  static propTypes = {
    errors: PropTypes.object,
    category: PropTypes.string.isRequired
  }

  render() {
    const errors = flatMap(this.props.errors, (message, field_name) => {
      return <li key={field_name + message}>{humanize(field_name)}: {message}</li>
    })

    return (
      <div className={`alert alert-${this.props.category}`}>
        <ul className="error-list">
          {errors}
        </ul>
      </div>
    )
  }
}
