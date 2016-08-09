import React, {PropTypes} from 'react'
import AvailabilityForm from './AvailabilityForm'
import CurrentAvailability from './CurrentAvailability'
import AvailabilityTable from './AvailabilityTable'

const availabilitySchema = PropTypes.shape({
  id: PropTypes.number.isRequired,
  start: PropTypes.string,
  quantity: PropTypes.number.isRequired
})

export default class AvailabilityManager extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      showForm: false
    }
  }

  static propTypes = {
    currentAvailability: availabilitySchema,
    upcomingAvailabilities: PropTypes.arrayOf(availabilitySchema).isRequired,
    onSubmitNew: PropTypes.func.isRequired
  }

  openForm() {
    this.setState({showForm: true})
  }

  closeForm() {
    this.setState({showForm: false})
  }

  renderForm() {
    if (this.state.showForm) {
      return <AvailabilityForm onCancel={this.closeForm.bind(this)} onSubmit={this.props.onSubmitNew} />
    } else {
      return <button className="btn btn-default" onClick={this.openForm.bind(this)}>Schedule a change</button>
    }
  }

  render() {
    return (
      <div>
        <CurrentAvailability availability={this.props.currentAvailability} />
        {this.props.upcomingAvailabilities.length == 0 ? null : <AvailabilityTable availabilities={this.props.upcomingAvailabilities} />}
        {this.renderForm()}
      </div>
    );
  }
}
