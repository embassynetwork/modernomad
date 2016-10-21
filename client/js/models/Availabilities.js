import _ from 'lodash'


export function isFullyAvailable(availabilities) {
  return !_.find(availabilities, (availability) => {
    return availability.quantity <= 0
  })
}
