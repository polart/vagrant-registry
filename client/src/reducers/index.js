import { combineReducers } from 'redux';
import { merge, isArray, set } from 'lodash';
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
    __all__: {
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
    switch (action.type) {
      case actionTypes.BOX.FETCH.SUCCESS:
        const username = action.username || (action.search && '__search__') || '__all__';
        const boxes = {};
        boxes[username] = action.response.pagination;
        boxes[username].pages = {};
        boxes[username].pages[action.response.pagination.page] = action.response.result;

        return merge(
            {},
            state,
            { boxes }
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

const initialForms = {
  box: {
    pending: false,
    data: {
      name: '',
      short_description: '',
      description: '',
      visibility: 'PT',
    },
    errors: {},
  },
};
function forms(state = initialForms, action) {
  let newState;
  let form = {};
  switch (action.type) {
    case actionTypes.FORM.SET_PENDING:
      form[action.model] = {
        pending: action.pending,
      };
      return merge(
          {},
          state,
          form
      );

    case actionTypes.FORM.FIELD_CHANGE:
      const modelPath = action.model.split('.');
      set(
          form,
          [modelPath[0], 'data', modelPath[1]],
          action.value
      );
      return merge(
          {},
          state,
          form
      );

    case actionTypes.FORM.SET_ERRORS:
      newState = merge({}, state);

      let { errors } = action;
      if (isArray(errors)) {
        errors = {
          non_field_errors: errors,
        }
      }
      newState[action.model].errors = errors;
      return newState;

    case actionTypes.FORM.CLEAR_ERRORS:
      newState = merge({}, state);
      newState[action.model].errors = {};
      return newState;

    case actionTypes.FORM.RESET:
      newState = merge({}, state);
      newState[action.model] = initialForms[action.model];
      return newState;

    default:
      return state
  }
}

const rootReducer = combineReducers({
  myUsername,
  entities,
  pagination,
  forms,
});

export default rootReducer;
