import React, {PropTypes} from 'react'
import ApolloClient from 'apollo-client'
import { ApolloProvider } from 'react-apollo'

const client = new ApolloClient();

class CurrentBackingDisplay extends React.Component {
  static propTypes = {
      rid: PropTypes.number.isRequired
  }

  renderCurrentBackers() {
    const backers = this.props.data.resource.currentBackersForDisplay

    if (this.props.data.loading) {
      return null
    } else {
      return (
        <div>
          <h5>Backed by ( return 
              backers.map(name) => {
                  return name
              }
          )
        </div>
      )
    }
  }

  render() {
    return (
      <Loader loading={this.props.data.loading}>
        {this.renderCurrentBackers()}
      </Loader>
    )
  }

}

export default class CurrentBacking extends React.Component {
  static propTypes = {
      resourceID: PropTypes.number.isRequired
  }

  render() {
    const {resourceID} = this.props
    return (
      <ApolloProvider client={client}>
        <CurrentBackingDisplay rid={resourceID} />
      </ApolloProvider>
    )
  }
}

const currentBackingQuery = gql`
  query getCurrentBackers($rid: ID!) {
    resource(id:$rid) {
      currentBackersForDisplay
    }
  }
`;

const CurrentBackingWithData = graphql(currentBackingsQuery)(CurrentBacking)

export default CurrentBackingsWithData
