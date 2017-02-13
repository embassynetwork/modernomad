import React, {PropTypes} from 'react'
import moment from 'moment'
import { graphql } from 'react-apollo'
import gql from 'graphql-tag'
import { Link } from 'react-router'
import { Panel, FormGroup, ControlLabel, FormControl, OverlayTrigger, Tooltip } from 'react-bootstrap';
import DatePicker from 'react-datepicker'
import Select from 'react-select'


class BackingForm extends React.Component {
  static propTypes = {
    mutate: PropTypes.func.isRequired,
    parent: PropTypes.object.isRequired,
    resource: PropTypes.number.isRequired

  }

  constructor(props) {
    super(props)
    this.state = {backers: [], start: moment()}

    this.handleChange = this.handleChange.bind(this)
    this.handleDateChange = this.handleDateChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
    this.handleUserChange = this.handleUserChange.bind(this)
  }

  handleChange(name) {
      return (event) => {
        const value = event.target.value
        this.setState({[name]:value})
      }
  }

  handleUserChange(value) {
    console.log(value)
    console.log('before',this.state)
    this.setState({backers:value})
    console.log('after',this.state)
      return (event) => {
        const value = event.value
        // this.setState({[name]:value})

      }
  }

  handleDateChange(event) {
    this.setState({start: event})
  }

  onSubmit(event) {
    event.preventDefault()
    const {mutate, resource, parent} = this.props
    const backersArr = []

    for (let i = 0; i < this.state.backers.length; i++) {
      backersArr.push(this.state.backers[i].value);
    }

    mutate({
        variables: {
            start:this.state.start.format("YYYY-MM-DDTHH:mm:ss.SSSSSS"),
            resource:resource,
            backers:backersArr
        }
      }).then(({ data }) => {
        console.log('got data', data)
        //parent.props.data.refetch();
        parent.refetch();
      }).catch((error) => {
        console.log('there was an error sending the query', error);
      });
  }

  allOptions() {
    const users = [];

    for (let i = 0; i < this.props.allUsers.length; i++) {
      users.push({
        value: this.props.allUsers[i].pk,
        label: `${this.props.allUsers[i].fields.first_name} ${this.props.allUsers[i].fields.last_name}`
      });
    }
    return users
  }

  getOptions = function(input, callback) {
    const options = this.allOptions()
    setTimeout(function() {
      callback(null, {
        options: options,
        complete: true
      });
    }, 200);
  };

  render() {
    return (
      <form className="backing-change-form form-inline" onSubmit={this.onSubmit.bind(this)}>
        <DatePicker className="form-control" name="start" selected={this.state.start} onChange={this.handleDateChange} />
        <Select.Async
          name="backers"
          loadOptions={this.getOptions.bind(this)}
          matchPos="start"
          value={this.state.backers}
          onChange={this.handleUserChange}
          multi={true}
        />
      <input className="form-control" type="submit" className="btn btn-primary" value="schedule" />
    </form>
    )
  }
}

const submitBacking = gql`
  mutation submitBacking($start: DateTime!, $resource: Int!, $backers: [Int]) {
    backing (start:$start, resource:$resource, backers:$backers) {
      ok
      backing {
        id
        start
        end
        users {
          edges {
            node {
              username
              id
            }
          }
        }
        resource {
          id
          name
        }
      }
    }
  }
`;


const BackingFormWithData = graphql(submitBacking)(BackingForm);
export default BackingFormWithData
