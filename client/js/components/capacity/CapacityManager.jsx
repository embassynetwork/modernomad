import React, {PropTypes} from 'react'
import CapacityForm from './CapacityForm'
import CurrentCapacity from './CurrentCapacity'
import CapacityTable from './CapacityTable'

const capacitySchema = PropTypes.shape({
  id: PropTypes.number.isRequired,
  start_date: PropTypes.string,
  quantity: PropTypes.number.isRequired,
  accept_drft: PropTypes.bool
})

export default class CapacityManager extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      showForm: false
    }
  }

  static propTypes = {
    currentCapacity: capacitySchema,
    upcomingCapacities: PropTypes.arrayOf(capacitySchema).isRequired,
    onSubmitNew: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    formLoading: PropTypes.bool
  }

  openForm() {
    this.setState({showForm: true})
  }

  closeForm() {
    this.setState({showForm: false})
  }

  renderForm() {
    if (this.state.showForm) {
      return <CapacityForm loading={this.props.formLoading} onCancel={this.closeForm.bind(this)} onSubmit={this.props.onSubmitNew} />
    } else {
      return <button className="btn btn-default" onClick={this.openForm.bind(this)}>Schedule a change</button>
    }
  }

  render() {
    return (
      <div>
        <CurrentCapacity capacity={this.props.currentCapacity} />
        {this.props.upcomingCapacities.length == 0 ? null : <CapacityTable onDelete={this.props.onDelete} capacities={this.props.upcomingCapacities} />}
        {this.renderForm()}
      </div>
    );
  }
}
