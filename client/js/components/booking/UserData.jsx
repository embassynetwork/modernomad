import React, {PropTypes} from 'react'
import { browserHistory } from 'react-router'
import RoomIndexOrDetail from './RoomIndexOrDetail'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import _ from 'lodash'
import moment from 'moment'
import Loader from '../generic/Loader'

const currentUserQuery = gql`
  query currentUserForAccounts {
    currentUser {
      edges {
        node {
          accountsOwned {
            edges {
              node {
                balance
                currency {
                  name
                }
              }
            }
          }
        }
      }
    }
  }
`;

class UserData extends React.Component {
  constructor(props) {
    super()
  }
  renderSubComponent() {
    const sharedProps = {
      ...this.props,
      loading: this.props.data.loading
    }

    return (
      <RoomIndexOrDetail {...sharedProps}>
      </RoomIndexOrDetail>
    )

  }

  render() {
    return (
      <Loader loading={this.props.data.loading}>
        {this.renderSubComponent()}
      </Loader>
    )
  }
}

const WithUserData = graphql(currentUserQuery)(UserData)
export default WithUserData
