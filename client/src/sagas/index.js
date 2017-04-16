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
const deleteBox = callRequest.bind(null, actions.box.delete, api.deleteBox);

const fetchBoxVersion = callRequest.bind(null, actions.boxVersion.fetch, api.fetchBoxVersion);
const fetchBoxVersions = callRequest.bind(null, actions.boxVersion.fetch, api.fetchBoxVersions);
const createBoxVersion = callRequest.bind(null, actions.boxVersion.create, api.createBoxVersion);
const editBoxVersion = callRequest.bind(null, actions.boxVersion.edit, api.editBoxVersion);
const deleteBoxVersion = callRequest.bind(null, actions.boxVersion.delete, api.deleteBoxVersion);

const createBoxProvider = callRequest.bind(null, actions.boxProvider.create, api.createBoxProvider);
const editBoxProvider = callRequest.bind(null, actions.boxProvider.edit, api.editBoxProvider);
const deleteBoxProvider = callRequest.bind(null, actions.boxProvider.delete, api.deleteBoxProvider);

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

export function* watchDeleteBox() {
  yield takeLatest(actionTypes.DELETE_BOX, function* ({tag}) {
    yield fork(deleteBox, {tag});

    const { success } = yield race({
      success: take(action => action.type === actionTypes.BOX.DELETE.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX.DELETE.FAILURE),
    });

    if (success) {
      browserHistory.push(`/`);
    }
  });
}

export function* watchFetchBoxVersion() {
  yield takeLatest(actionTypes.LOAD_BOX_VERSION, fetchBoxVersion)
}

export function* watchFetchBoxVersions() {
  yield takeLatest(actionTypes.LOAD_BOX_VERSIONS, fetchBoxVersions)
}

export function* watchCreateBoxVersion() {
  yield takeLatest(actionTypes.CREATE_BOX_VERSION, function* ({tag, data}) {
    yield put(actions.form.setPending('boxVersion', true));
    yield fork(createBoxVersion, {tag, data});

    const { success, failure } = yield race({
      success: take(action => action.type === actionTypes.BOX_VERSION.CREATE.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX_VERSION.CREATE.FAILURE),
    });

    if (failure) {
      yield put(actions.form.setErrors('boxVersion', failure.error));
      yield put(actions.form.setPending('boxVersion', false));
    } else if (success) {
      yield put(actions.form.reset('boxVersion'));
      browserHistory.push(`/boxes/${tag}/versions/`);
    }
  });
}

export function* watchEditBoxVersion() {
  yield takeLatest(actionTypes.EDIT_BOX_VERSION, function* ({tag, version, data}) {
    yield put(actions.form.setPending('boxVersion', true));
    yield fork(editBoxVersion, {tag, version, data});

    const { success, failure } = yield race({
      success: take(action => action.type === actionTypes.BOX_VERSION.EDIT.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX_VERSION.EDIT.FAILURE),
    });

    if (failure) {
      yield put(actions.form.setErrors('boxVersion', failure.error));
      yield put(actions.form.setPending('boxVersion', false));
    } else if (success) {
      yield put(actions.form.reset('boxVersion'));
      browserHistory.push(`/boxes/${tag}/versions/${data.version}/`);
    }
  });
}

export function* watchDeleteBoxVersion() {
  yield takeLatest(actionTypes.DELETE_BOX_VERSION, function* ({tag, version}) {
    yield fork(deleteBoxVersion, {tag, version});

    const { success } = yield race({
      success: take(action => action.type === actionTypes.BOX_VERSION.DELETE.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX_VERSION.DELETE.FAILURE),
    });

    if (success) {
      browserHistory.push(`/boxes/${tag}/versions/`);
    }
  });
}

export function* watchCreateBoxProvider() {
  yield takeLatest(actionTypes.CREATE_BOX_PROVIDER, function* ({tag, version, data}) {
    yield put(actions.form.setPending('boxProvider', true));
    yield fork(createBoxProvider, {tag, version, data});

    const { success, failure } = yield race({
      success: take(action => action.type === actionTypes.BOX_PROVIDER.CREATE.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX_PROVIDER.CREATE.FAILURE),
    });

    if (failure) {
      yield put(actions.form.setErrors('boxProvider', failure.error));
      yield put(actions.form.setPending('boxProvider', false));
    } else if (success) {
      yield put(actions.form.reset('boxProvider'));
      browserHistory.push(`/boxes/${tag}/versions/${version}/`);
    }
  });
}

export function* watchEditBoxProvider() {
  yield takeLatest(actionTypes.EDIT_BOX_PROVIDER, function* ({tag, version, provider, data}) {
    yield put(actions.form.setPending('boxProvider', true));
    yield fork(editBoxProvider, {tag, version, provider, data});

    const { success, failure } = yield race({
      success: take(action => action.type === actionTypes.BOX_PROVIDER.EDIT.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX_PROVIDER.EDIT.FAILURE),
    });

    if (failure) {
      yield put(actions.form.setErrors('boxProvider', failure.error));
      yield put(actions.form.setPending('boxProvider', false));
    } else if (success) {
      yield put(actions.form.reset('boxProvider'));
      browserHistory.push(`/boxes/${tag}/versions/${version}/`);
    }
  });
}

export function* watchDeleteBoxProvider() {
  yield takeLatest(actionTypes.DELETE_BOX_PROVIDER, function* ({tag, version, provider}) {
    yield fork(deleteBoxProvider, {tag, version, provider});

    const { success } = yield race({
      success: take(action => action.type === actionTypes.BOX_PROVIDER.DELETE.SUCCESS),
      failure: take(action => action.type === actionTypes.BOX_PROVIDER.DELETE.FAILURE),
    });

    if (success) {
      yield put(actions.loadBoxVersion(tag, version));
      // browserHistory.push(`/boxes/${tag}/versions/${version}/`);
    }
  });
}


export default function* rootSaga() {
  yield [
    watchFetchUser(),
    watchFetchUsers(),

    watchFetchBox(),
    watchFetchBoxes(),
    watchCreateBox(),
    watchEditBox(),
    watchDeleteBox(),

    watchFetchBoxVersion(),
    watchFetchBoxVersions(),
    watchCreateBoxVersion(),
    watchEditBoxVersion(),
    watchDeleteBoxVersion(),

    watchCreateBoxProvider(),
    watchEditBoxProvider(),
    watchDeleteBoxProvider(),
  ]
}
