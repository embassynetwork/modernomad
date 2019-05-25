import React from 'react'
import ReactLoaderAdvanced from 'react-loader-advanced'
import CircularProgress from 'material-ui/CircularProgress';

function Loader(props) {
  return (
    <ReactLoaderAdvanced
      show={!!props.loading}
      backgroundStyle={{backgroundColor: '#FFFFFF', opacity: 0.7}}
      message={<CircularProgress />}
      hideContentOnLoad={true}
    >
      {props.children}
    </ReactLoaderAdvanced>
  )
}

export default Loader
