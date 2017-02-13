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

    const backers = currentBackers.map((u, i, arr) => {
      const { id, username, firstName, lastName } = u
      return (
        <a key={id} href={`/people/${username}`}>
          {firstName} {lastName}{(i !== arr.length -1)?', ':''}
        </a>
      )
    })
    
    const html = currentBackers.length > 0 ? backers : "no one."
    return (
      <div>
        <h5> Currently backed by {html} </h5>
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
