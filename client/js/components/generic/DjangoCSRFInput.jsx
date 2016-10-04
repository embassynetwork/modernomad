import React from 'react'
import Cookies from 'js-cookie'

export default function DjangoCSRFInput(props) {
  const token = Cookies.get('csrftoken')
  return <input type="hidden" name="csrfmiddlewaretoken" value={token} />
}
