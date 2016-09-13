import React, {PropTypes} from 'react'


export default class RoomDetail extends React.Component {

  render() {

    return (
      <div>{this.props.params.id}</div>
    )

  }
}
