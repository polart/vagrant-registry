import {call, fork, put, race, take, takeLatest} from "redux-saga/effects";
import * as api from "../api";
import {browserHistory} from "react-router";
import * as actionTypes from "../actions/types";
import * as actions from "../actions";


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
    if (status === 401) {
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
const createBox = callRequest.bind(null, actions.box.create, api.createBox);
const editBox = callRequest.bind(null, actions.box.edit, api.editBox);
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

export function* watchCreateBox() {
  yield takeLatest(actionTypes.CREATE_BOX, function* ({username, data}) {
    yield put(actions.form.setPending('box', true));
    yield fork(createBox, {username, data});

    const { success, failure } = yield race({
      success: take(action => action.type === actionTypes.BOX.CREATE.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX.CREATE.FAILURE),
    });

    if (failure) {
      yield put(actions.form.setErrors('box', failure.error));
      yield put(actions.form.setPending('box', false));
    } else if (success) {
      yield put(actions.form.reset('box'));
      browserHistory.push(`/boxes/${username}/${data.name}/`);
    }
  });
}

export function* watchEditBox() {
  yield takeLatest(actionTypes.EDIT_BOX, function* ({tag, data}) {
    yield put(actions.form.setPending('box', true));
    yield fork(editBox, {tag, data});

    const { success, failure } = yield race({
      success: take(action => action.type === actionTypes.BOX.EDIT.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX.EDIT.FAILURE),
    });

    if (failure) {
      yield put(actions.form.setErrors('box', failure.error));
      yield put(actions.form.setPending('box', false));
    } else if (success) {
      yield put(actions.form.reset('box'));
      browserHistory.push(`/boxes/${data.owner}/${data.name}/`);
    }
  });
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
      watchCreateBox(),
      watchEditBox(),
      watchFetchBoxVersion(),
      watchFetchBoxVersions(),
  ]
}
