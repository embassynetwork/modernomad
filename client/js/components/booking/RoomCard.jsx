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
      <div className="col-md-4 room-thumbnail">
        <div className="panel panel-default">
          <div className="panel-body">

            <ImageCarousel img={this.props.img} />
            <Link className="col-xs-12" to={{pathname:`/locations/${this.props.routeParams.location}/stay/room/${this.props.id}`, query: this.props.query}}>
              <h3>{this.props.name} <span className="pull-right room-cost"><b>${this.props.cost} / night</b></span></h3>
              <div className="row text-center room-tags">
                { this.props.type == "Shared Room" ?
                  <div className="col-xs-6"><i className="fa fa-unlock-alt fa-2x"></i><br></br>{this.props.type}</div>
                  :
                  <div className="col-xs-6"><i className="fa fa-lock fa-2x"></i><br></br>{this.props.type}</div>
                }
                { this.props.guests == "1" ?
                  <div className="col-xs-6"><i className="fa fa-user fa-2x"></i><br></br>{this.props.guests} Guest</div>
                  :
                  <div className="col-xs-6"><i className="fa fa-users fa-2x"></i><br></br>{this.props.guests} Guests</div>
                }
              </div>
            </Link>
          </div>
        </div>
      </div>
    )
  }
}
