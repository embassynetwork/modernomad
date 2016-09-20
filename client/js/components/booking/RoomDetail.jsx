import React, {PropTypes} from 'react'
import DateRangeSelector from './DateRangeSelector'
import ImageCarousel from './ImageCarousel'


const hardcodedRooms = [
  {id: 1, name: "lovelace", cost:"150", summary:"Ennui before they sold out dreamcatcher woke gochujang. Fam lyft franzen messenger bag fixie prism yuccie microdosing letterpress hot chicken selfies brunch kale chips venmo. Bicycle rights helvetica organic gluten-free hot chicken cornhole.", type:"Private Room", guests:"2", img: ["/media/rooms/82c1da3f-67d2-443e-850f-c76a3639e063.png", "/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 2, name: "flyut", cost:"55", summary:"Ennui before they sold out dreamcatcher woke gochujang. Fam lyft franzen messenger bag fixie prism yuccie microdosing letterpress hot chicken selfies brunch kale chips venmo. Bicycle rights helvetica organic gluten-free hot chicken cornhole.", type: "Shared Room", guests:"1", img: ["/media/rooms/ed6e58fa-df9f-4e94-848e-7f402516421e.png", "/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 3, name: "fishbowl", cost:"100", summary:"Ennui before they sold out dreamcatcher woke gochujang. Fam lyft franzen messenger bag fixie prism yuccie microdosing letterpress hot chicken selfies brunch kale chips venmo. Bicycle rights helvetica organic gluten-free hot chicken cornhole.", type: "Shared Room", guests:"3", img: ["/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 4, name: "golden age", cost:"110", summary:"Ennui before they sold out dreamcatcher woke gochujang. Fam lyft franzen messenger bag fixie prism yuccie microdosing letterpress hot chicken selfies brunch kale chips venmo. Bicycle rights helvetica organic gluten-free hot chicken cornhole.", type: "Shared Room", guests:"4", img: ["/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png", "/media/rooms/ed6e58fa-df9f-4e94-848e-7f402516421e.png"]},
]

export default class RoomDetail extends React.Component {

  constructor(props) {
    super(props)

    this.state = {rooms: hardcodedRooms}
  }

  render() {

    return (
      <div className="row">
        <div className="col-sm-8">
          <h1>{this.state.rooms[this.props.params.id].name}</h1>
          <p>{this.state.rooms[this.props.params.id].summary}</p>
          <ImageCarousel img={this.state.rooms[this.props.params.id-1].img} />
        </div>
        <div className="col-sm-4">
          <DateRangeSelector />
          <div className="alert alert-success">These dates are available</div>
          <p>${this.state.rooms[this.props.params.id].cost}*nights<span className="pull-right">$</span></p>
          <hr></hr>
          <p>SF Hotel Taxes <span className="pull-right">$</span></p>
          <hr></hr>
          <p><b>Total<span className="pull-right">$</span></b></p>
          <p>*Tell us a little about the purpose of your trip</p>
          <textarea className="form-control"></textarea>
          <p>Arrival time</p>
          <input className="form-control" type="time"></input>
          <button className="btn btn-primary btn-block">Request</button>
        </div>
      </div>
    )

  }
}
