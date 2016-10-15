import React, {PropTypes} from 'react'
import { Carousel } from 'react-bootstrap';
import { CarouselItem } from 'react-bootstrap';

export default class ImageCarousel extends React.Component {

  static propTypes = {
    img: PropTypes.array.isRequired
  }


  render() {
    var item = this.props.img.map((img) => {
      return(
        <CarouselItem key={img}>
          <img src={img} />
        </CarouselItem>
      )
    })
    return (
      <Carousel indicators={false} interval={0}>
        {item}
      </Carousel>
    )
  }
}
