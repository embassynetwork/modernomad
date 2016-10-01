import React, {PropTypes} from 'react'
import { Link } from 'react-router'
import ImageCarousel from './ImageCarousel'
import _ from 'lodash'


export default class RoomCard extends React.Component {
  static propTypes = {
    name: PropTypes.string.isRequired
  }

  detailUrl() {
    return `/locations/${this.props.routeParams.location}/stay/room/${this.props.rid}`
  }

  detailLinkDetails() {
    return {pathname: this.detailUrl(), query: this.props.query}
  }

  render() {
    return (
      <div className="col-md-4 col-sm-6 room-thumbnail">
        <div className="panel panel-default">
          <div className="panel-body">

            {/*this.props.image && <ImageCarousel img={this.props.image} />*/}
            <img className="room-image" src={"/media/"+this.props.image} />
            <Link className="col-xs-12" to={this.detailLinkDetails()}>
              <h3>{this.props.name}</h3>
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
            </Link>
          </div>
        </div>
      </div>
    )
  }
}
