import { combineReducers } from 'redux';
import { merge } from 'lodash';

import * as actionTypes from '../actions/types';


const initialStateEntities = {
  users: {},
  boxes: {},
};

// Updates an entity cache in response to any action with response.entities.
function entities(state = initialStateEntities, action) {
  if (action.response && action.response.entities) {
    return merge({}, state, action.response.entities)
  }
  return state;
}

function myUsername(state = null, action) {
  switch (action.type) {
    case actionTypes.SET_MY_USERNAME:
      return action.username;
    default:
      return state
  }
}

const rootReducer = combineReducers({
  myUsername,
  entities,
});

export default rootReducer;
