import React, {PropTypes} from 'react'
import moment from 'moment'
import { graphql } from 'react-apollo'
import gql from 'graphql-tag'
import { Link } from 'react-router'
import { Panel, FormGroup, ControlLabel, FormControl, OverlayTrigger, Tooltip } from 'react-bootstrap';
import DatePicker from 'react-datepicker'

class BackingForm extends React.Component {
  constructor(props) {
    super(props)
    this.state = {backers: [], start: moment()}

    this.handleChange = this.handleChange.bind(this)
    this.handleDateChange = this.handleDateChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
  }

  handleChange(name) {
      return (event) => {
        const value = event.target.value
        this.setState({[name]:value})
      }
  }

  handleDateChange(event) {
    this.setState({start: event})
  }

  onSubmit(event) {
    event.preventDefault()
    this.props.mutate({ variables: { start:this.state.start.format("YYYY-MM-DDTHH:mm:ss.SSSSSS"), resource:this.props.resource, backers:this.state.backers.split(",") } })
      .then(({ data }) => {
        console.log('got data', data);
      }).catch((error) => {
        console.log('there was an error sending the query', error);
      });
  }


// 2017-02-20T21:34:11.721016
  render() {
    return (
      <form className="backing-change-form form-inline" onSubmit={this.onSubmit.bind(this)}>
        <DatePicker className="form-control" name="start" selected={this.state.start} onChange={this.handleDateChange} />
        <input className="form-control" type="input" name="backers" onChange={this.handleChange('backers')} />
        <input className="form-control" type="submit" className="btn btn-primary" value="schedule" />
      </form>
    )
  }
}

BackingForm.propTypes = {
  mutate: PropTypes.func.isRequired,
};

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
