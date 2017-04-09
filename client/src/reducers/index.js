import { combineReducers } from 'redux';
import { merge } from 'lodash';

import * as actionTypes from '../actions/types';


const initialStateEntities = {
  users: {},
  boxes: {},
  boxVersions: {},
  boxProviders: {},
};

function entities(state = initialStateEntities, action) {
  if (action.response && action.response.entities) {
    return merge({}, state, action.response.entities)
  }
  return state;
}

const initialStatePagination = {
  users: {},
  boxes: {
    __all: {
      count: 0,
      activePage: 1,
      pages: {},
    }
  },
  boxVersions: {},
};

function pagination(state = initialStatePagination, action) {
  if (action.response
      && action.response.entities
      && action.response.pagination
      && action.response.pagination.page
  ) {
    console.log('response -- ', action);
    let pages;
    switch (action.type) {
      case actionTypes.BOX.FETCH.SUCCESS:
        pages = {};
        pages[action.response.pagination.page] = action.response.result;

        return merge(
            {},
            state,
            {boxes: {
              __all: {
                count: action.response.pagination.count,
                pages,
              }
            }}
        );
      case actionTypes.BOX_VERSION.FETCH.SUCCESS:
        const boxVersions = {};
        boxVersions[action.tag] = action.response.pagination;
        boxVersions[action.tag].pages = {};
        boxVersions[action.tag].pages[action.response.pagination.page] = action.response.result;

        return merge(
            {},
            state,
            { boxVersions }
        );
      default:
        return state
    }
    // return merge({}, state, action.response.pagination)
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
  pagination,
});

export default rootReducer;
