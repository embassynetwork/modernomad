import React, {PropTypes} from 'react'
import ApolloClient from 'apollo-client'
import { ApolloProvider } from 'react-apollo'
import gql from 'graphql-tag'
import { graphql } from 'react-apollo'
import Loader from '../generic/Loader'

const client = new ApolloClient();

class CurrentBackingDisplay extends React.Component {
static propTypes = {
    currentBackers: PropTypes.array.isRequired
}

  render() {
    const {currentBackers} = this.props
    return (
      <div>
        <h5>
        Backed by
          { currentBackers.map((u) => {
              return <span key={u.id}> {u.firstName} {u.lastName}</span>
            })
          }
        </h5>
      </div>
    )
  }

}

class CurrentBackingWithoutData extends React.Component {
  static propTypes = {
      resourceID: PropTypes.number.isRequired,
      parent: PropTypes.object.isRequired
  }


  render() {
    const {parent, data} = this.props
    parent.state.currentBackersData = data
    const {resource, loading} = data
    if (loading) {
      return null
    } else {
      return <CurrentBackingDisplay currentBackers={resource.currentBackers}/>
    }
  }
}

const currentBackingQuery = gql`
  query getCurrentBackers($resourceID: ID!) {
    resource(id:$resourceID) {
      currentBackers {
        id
        username
        firstName
        lastName
      }
    }
  }
`;

const CurrentBacking = graphql(currentBackingQuery)(CurrentBackingWithoutData)
export default CurrentBacking 
