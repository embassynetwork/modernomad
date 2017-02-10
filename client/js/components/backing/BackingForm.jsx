import React, {PropTypes} from 'react'
import moment from 'moment'
import { graphql } from 'react-apollo'
import gql from 'graphql-tag'
import { Link } from 'react-router'
import { Panel, FormGroup, ControlLabel, FormControl, OverlayTrigger, Tooltip } from 'react-bootstrap';

export default class BackingForm extends React.Component {
  static propTypes = {

  }

  constructor(props) {
    super(props)
  }

  onSubmit() {
    this.props.mutate({ variables: { start:"2017-02-20", resource:8, backers:[1] } })
      .then(({ data }) => {
        console.log('got data', data);
      }).catch((error) => {
        console.log('there was an error sending the query', error);
      });
  }

  render() {

    return (
      <a className="backing-change-form" onClick={this.onSubmit.bind(this)}>
        click me
      </a>
    )

  }
}

BackingForm.propTypes = {
  mutate: PropTypes.func.isRequired,
};

const submitBacking = gql`
  mutation submitBacking {
    backing (start:"2017-02-20", resource:8, backers:[1]) {
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

const BackingFormWithData = graphql(submitBacking, {
  // props: ({ mutate }) => ({
  //   submit: (start, resource, backers) => mutate({ variables: { start, resource, backers } }),
  // }),
})(BackingForm);

// const NewEntryWithData = graphql(submitRepository, {
//   props: ({ mutate }) => ({
//     submit: (repoFullName) => mutate({ variables: { repoFullName } }),
//   }),
// })(NewEntry);
