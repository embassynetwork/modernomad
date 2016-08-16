import React, {PropTypes} from 'react'
import ReactDom from 'react-dom'

export default class DatePicker extends React.Component {
	componentDidMount() {
		const element = ReactDom.findDOMNode(this)
		$(element).datepicker({
			dateFormat: "yy-mm-dd"
		})
    }
    
	value() {
		return ReactDom.findDOMNode(this).value
	}

	render() {
		return <input type="text" {...this.props} />
	}

}


