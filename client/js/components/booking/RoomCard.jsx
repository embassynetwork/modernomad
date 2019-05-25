import React, {PropTypes} from 'react'
import { Link } from 'react-router-dom'
import ImageCarousel from './ImageCarousel'
import _ from 'lodash'


export default class RoomCard extends React.Component {
  static propTypes = {
    name: PropTypes.string.isRequired
  }

  detailLinkDetails() {
    return {
      pathname: `/locations/${this.props.location_name}/stay/room/${this.props.id}`,
      query: this.props.query
    }
  }

  render() {
    let path = `/locations/${this.props.location_name}/edit/rooms/${this.props.id}`

    return (
      <div className="col-lg-4 col-sm-6 room-card">
        {this.props.isAdmin ?
          <a href={path} className="edit-room btn btn-default">Edit</a>
          :
          <span></span>
        }
        <Link to={this.detailLinkDetails()} target={(this.props.drft ? "_blank" : "")} className="room-link">
          <div className="panel panel-default">
            <div className="panel-body">
              <img className="room-image img-responsive" src={this.props.image} />
              <div className="col-xs-12">
                <h3>{this.props.name}</h3>
                {this.props.hasFutureDrftCapacity ?
                  <span className="pull-left accepts-drft"><b>Accepts Ɖ</b></span>
                  :
                  <span></span>
                }
                <span className="pull-right room-cost"><b>${this.props.default_rate} / night</b></span>
              </div>
            </div>
          </div>
        </Link>
      </div>
    )
  }
}
