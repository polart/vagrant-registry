import { takeLatest } from 'redux-saga'
import { call, put, take, spawn, race, actionChannel, fork } from 'redux-saga/effects'
import { delay } from 'redux-saga'
import * as api from '../api';
import {actions as formActions} from 'react-redux-form';
import { browserHistory } from 'react-router';
import * as actionTypes from '../actions/types';
import * as actions from '../actions';


//*********************************************************
// Subroutines
//*********************************************************

function* callRequest(entity, apiFn, data = null) {
  yield put( entity.request(data) );
  const {response, error, status} = yield call(apiFn, data);
  if (response) {
    yield put(entity.success(data, response));
  }
  else {
    yield put(entity.failure(data, error));
    if (status === 403) {
      localStorage.removeItem('token');
      localStorage.removeItem('state');
      browserHistory.push('/');
    }
  }
}


const fetchUser = callRequest.bind(null, actions.user.fetch, api.fetchUser);
const fetchUsers = callRequest.bind(null, actions.user.fetch, api.fetchUsers);
const fetchBoxes = callRequest.bind(null, actions.box.fetch, api.fetchBoxes);

//*********************************************************
// Watchers
//*********************************************************

export function* watchFetchUser() {
  yield* takeLatest(actionTypes.LOAD_USER, fetchUser)
}

export function* watchFetchUsers() {
  yield* takeLatest(actionTypes.LOAD_USERS, fetchUsers)
}

export function* watchFetchBoxes() {
  yield* takeLatest(actionTypes.LOAD_BOXES, fetchBoxes)
}


export default function* rootSaga() {
  yield [
      watchFetchUser(),
      watchFetchUsers(),
      watchFetchBoxes(),
  ]
}
