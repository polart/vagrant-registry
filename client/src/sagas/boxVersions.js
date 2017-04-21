import {call, put, takeLatest} from "redux-saga/effects";
import * as api from "../api";
import {browserHistory} from "react-router";
import * as actionTypes from "../actions/types";
import * as actions from "../actions";
import {callRequest} from "./utils";


const fetchBoxVersion = callRequest.bind(null, actions.boxVersion.fetch, api.fetchBoxVersion);
const fetchBoxVersions = callRequest.bind(null, actions.boxVersion.fetch, api.fetchBoxVersions);
const createBoxVersion = callRequest.bind(null, actions.boxVersion.create, api.createBoxVersion);
const editBoxVersion = callRequest.bind(null, actions.boxVersion.edit, api.editBoxVersion);
const deleteBoxVersion = callRequest.bind(null, actions.boxVersion.delete, api.deleteBoxVersion);


export function* watchFetchBoxVersion() {
  yield takeLatest(actionTypes.LOAD_BOX_VERSION, fetchBoxVersion)
}

export function* watchFetchBoxVersions() {
  yield takeLatest(actionTypes.LOAD_BOX_VERSIONS, fetchBoxVersions)
}

export function* watchCreateBoxVersion() {
  yield takeLatest(actionTypes.CREATE_BOX_VERSION, function* ({tag, data}) {
    yield put(actions.form.setPending('boxVersion', true));
    const { response, error } = yield call(createBoxVersion, {tag, data});

    if (error) {
      yield put(actions.form.setErrors('boxVersion', error));
      yield put(actions.form.setPending('boxVersion', false));
    } else if (response) {
      yield put(actions.form.reset('boxVersion'));
      browserHistory.push(`/boxes/${tag}/versions/`);
    }
  });
}

export function* watchEditBoxVersion() {
  yield takeLatest(actionTypes.EDIT_BOX_VERSION, function* ({tag, version, data}) {
    yield put(actions.form.setPending('boxVersion', true));
    const { response, error } = yield call(editBoxVersion, {tag, version, data});

    if (error) {
      yield put(actions.form.setErrors('boxVersion', error));
      yield put(actions.form.setPending('boxVersion', false));
    } else if (response) {
      yield put(actions.form.reset('boxVersion'));
      browserHistory.push(`/boxes/${tag}/versions/${data.version}/`);
    }
  });
}

export function* watchDeleteBoxVersion() {
  yield takeLatest(actionTypes.DELETE_BOX_VERSION, function* ({tag, version}) {
    const { response } = yield call(deleteBoxVersion, {tag, version});

    if (response) {
      browserHistory.push(`/boxes/${tag}/versions/`);
    }
  });
}

export default [
  watchFetchBoxVersion,
  watchFetchBoxVersions,
  watchCreateBoxVersion,
  watchEditBoxVersion,
  watchDeleteBoxVersion,
];
