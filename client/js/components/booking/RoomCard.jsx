import React, {PropTypes} from 'react'
import { Link } from 'react-router'
import ImageCarousel from './ImageCarousel'
import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import _ from 'lodash'


export default class RoomCard extends React.Component {
  static propTypes = {
    name: PropTypes.string.isRequired
  }

  detailLinkDetails() {
    return {
      pathname: `/locations/${this.props.routeParams.location}/stay/room/${this.props.rid}`,
      query: this.props.query
    }
  }

  render() {

    const editTooltip = (
      <Tooltip id="tooltip">Edit {this.props.name}</Tooltip>
    );

    return (
      <div className="col-lg-4 col-sm-6 room-card">
        {this.props.route.isAdmin ?
          <a href={"/locations/"+this.props.routeParams.location+"/edit/rooms/"+this.props.rid} target="_blank" className="edit-room">
            <OverlayTrigger placement="top" overlay={editTooltip}>
              <span className="fa fa-pencil fa-2x"></span>
            </OverlayTrigger>
          </a>
          :
          <span></span>
        }
        <Link to={this.detailLinkDetails()} target={(this.props.drft ? "_blank" : "")} className="room-link">
          <div className="panel panel-default">
            <div className="panel-body">

              {/*this.props.image && <ImageCarousel img={this.props.image} />*/}
              <img className="room-image img-responsive" src={"/media/"+this.props.image} />
              <div className="col-xs-12">
                <h3>{this.props.name}</h3>
                {this.props.hasFutureDrftCapacity ?
                  <span className="pull-left accepts-drft"><b>Accepts Ɖ</b></span>
                  :
                  <span></span>
                }
                <span className="pull-right room-cost"><b>${this.props.defaultRate} / night</b></span>
                {/*}<div className="row text-center room-tags">
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
                </div>*/}
              </div>
            </div>
          </div>
        </Link>
      </div>
    )
  }
}
