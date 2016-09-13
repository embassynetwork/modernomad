import React, {PropTypes} from 'react'
import { Link } from 'react-router'
import ImageCarousel from './ImageCarousel'

export default class RoomCard extends React.Component {

  static propTypes = {
    name: PropTypes.string.isRequired,
    img: PropTypes.array.isRequired
  }

  render() {
    return (
      <div className="col-md-4">
        <ImageCarousel img={this.props.img}/>
        <Link to={`/locations/${this.props.routeParams.location}/stay/room/${this.props.id}`}><h3>{this.props.name} <span className="pull-right">${this.props.cost}</span></h3></Link>
        <p><em>{this.props.type} • {this.props.guests} Guests</em></p>
      </div>
    )
  }
}
