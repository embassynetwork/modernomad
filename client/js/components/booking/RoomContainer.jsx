import React, {PropTypes} from 'react'
import RoomIndex from './RoomIndex'

const hardcodedRooms = [
  {id: 1, name: "lovelace", cost:"150", type:"Private Room", guests:"2", img: ["/media/rooms/82c1da3f-67d2-443e-850f-c76a3639e063.png", "/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 2, name: "flyut", cost:"55", type: "Shared Room", guests:"1", img: ["/media/rooms/ed6e58fa-df9f-4e94-848e-7f402516421e.png", "/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 3, name: "fishbowl", cost:"100", type: "Shared Room", guests:"3", img: ["/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 4, name: "golden age", cost:"110", type: "Shared Room", guests:"4", img: ["/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png", "/media/rooms/ed6e58fa-df9f-4e94-848e-7f402516421e.png"]},
]

export default class RoomContainer extends React.Component {
  constructor(props) {
    super(props)

    this.state = {rooms: hardcodedRooms}
  }

  triggerChange(arrive, depart) {
    this.setState({rooms: []})
  }

  render() {
    return <RoomIndex rooms={this.state.rooms} routeParams={this.props.routeParams} onChange={this.triggerChange.bind(this)} />
  }
}
