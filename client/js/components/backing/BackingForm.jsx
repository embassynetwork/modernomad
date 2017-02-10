import React, {PropTypes} from 'react'
import moment from 'moment'
import { graphql } from 'react-apollo'
import gql from 'graphql-tag'
import { Link } from 'react-router'
import { Panel, FormGroup, ControlLabel, FormControl, OverlayTrigger, Tooltip } from 'react-bootstrap';

class BackingForm extends React.Component {
  constructor(props) {
    super(props)
    this.state = {backers: "", start: ""}

    this.handleChange = this.handleChange.bind(this)
    this.onSubmit = this.onSubmit.bind(this)
  }

  handleChange(name) {
      return (event) => {
        const value = event.target.value
        this.setState({[name]:value})
      }
  }

  onSubmit(event) {
    event.preventDefault()
    this.props.mutate({ variables: { start:this.state.start, resource:this.props.resource, backers:this.state.backers } })
      .then(({ data }) => {
        console.log('got data', data);
      }).catch((error) => {
        console.log('there was an error sending the query', error);
      });
  }


// 2017-02-20T21:34:11.721016
  render() {
    return (
      <form className="backing-change-form" onSubmit={this.onSubmit.bind(this)}>
        <input type="input" name="start" onChange={this.handleChange('start')} />
        <input type="input" name="backers" />
        <input type="submit" className="btn btn-primary" value="schedule" />
      </form>
    )
  }
}

BackingForm.propTypes = {
  mutate: PropTypes.func.isRequired,
};

const submitBacking = gql`
  mutation submitBacking($start: DateTime!, $resource: Int!, $backers: [Int!]) {
    backing (start:$start, resource:$resource, backers:$backers) {
      ok
      backing {
        id
        start
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
