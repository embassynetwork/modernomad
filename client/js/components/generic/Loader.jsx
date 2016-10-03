import React from 'react'
import ReactLoaderAdvanced from 'react-loader-advanced'


function Loader(props) {
  return (
    <ReactLoaderAdvanced show={props.loading} backgroundStyle={{backgroundColor: '#FFFFFF', opacity: 0.7}}>
      {props.children}
    </ReactLoaderAdvanced>
  )
}

export default Loader
