import { call, put, takeLatest } from 'redux-saga/effects'
import * as api from '../api';
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
const fetchBox = callRequest.bind(null, actions.box.fetch, api.fetchBox);
const fetchBoxes = callRequest.bind(null, actions.box.fetch, api.fetchBoxes);
const fetchBoxVersion = callRequest.bind(null, actions.boxVersion.fetch, api.fetchBoxVersion);
const fetchBoxVersions = callRequest.bind(null, actions.boxVersion.fetch, api.fetchBoxVersions);

//*********************************************************
// Watchers
//*********************************************************

export function* watchFetchUser() {
  yield takeLatest(actionTypes.LOAD_USER, fetchUser)
}

export function* watchFetchUsers() {
  yield takeLatest(actionTypes.LOAD_USERS, fetchUsers)
}

export function* watchFetchBox() {
  yield takeLatest(actionTypes.LOAD_BOX, fetchBox)
}

export function* watchFetchBoxes() {
  yield takeLatest(actionTypes.LOAD_BOXES, fetchBoxes)
}

export function* watchFetchBoxVersion() {
  yield takeLatest(actionTypes.LOAD_BOX_VERSION, fetchBoxVersion)
}

export function* watchFetchBoxVersions() {
  yield takeLatest(actionTypes.LOAD_BOX_VERSIONS, fetchBoxVersions)
}


export default function* rootSaga() {
  yield [
      watchFetchUser(),
      watchFetchUsers(),
      watchFetchBox(),
      watchFetchBoxes(),
      watchFetchBoxVersion(),
      watchFetchBoxVersions(),
  ]
}
