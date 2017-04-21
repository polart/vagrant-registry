import {call, put, takeLatest} from "redux-saga/effects";
import * as api from "../api";
import {browserHistory} from "react-router";
import * as actionTypes from "../actions/types";
import * as actions from "../actions";
import {callRequest} from "./utils";


const fetchBox = callRequest.bind(null, actions.box.fetch, api.fetchBox);
const fetchBoxes = callRequest.bind(null, actions.box.fetch, api.fetchBoxes);
const createBox = callRequest.bind(null, actions.box.create, api.createBox);
const editBox = callRequest.bind(null, actions.box.edit, api.editBox);
const deleteBox = callRequest.bind(null, actions.box.delete, api.deleteBox);


export function* watchFetchBox() {
  yield takeLatest(actionTypes.LOAD_BOX, fetchBox)
}

export function* watchFetchBoxes() {
  yield takeLatest(actionTypes.LOAD_BOXES, fetchBoxes)
}

export function* watchCreateBox() {
  yield takeLatest(actionTypes.CREATE_BOX, function* ({username, data}) {
    yield put(actions.form.setPending('box', true));
    const { response, error } = yield call(createBox, {username, data});

    if (error) {
      yield put(actions.form.setErrors('box', error));
      yield put(actions.form.setPending('box', false));
    } else if (response) {
      yield put(actions.form.reset('box'));
      browserHistory.push(`/boxes/${username}/${data.name}/`);
    }
  });
}

export function* watchEditBox() {
  yield takeLatest(actionTypes.EDIT_BOX, function* ({tag, data}) {
    yield put(actions.form.setPending('box', true));
    const { response, error } = yield call(editBox, {tag, data});

    if (error) {
      yield put(actions.form.setErrors('box', error));
      yield put(actions.form.setPending('box', false));
    } else if (response) {
      yield put(actions.form.reset('box'));
      browserHistory.push(`/boxes/${data.owner}/${data.name}/`);
    }
  });
}

export function* watchDeleteBox() {
  yield takeLatest(actionTypes.DELETE_BOX, function* ({tag}) {
    const { response } = yield call(deleteBox, {tag});

    if (response) {
      browserHistory.push(`/`);
    }
  });
}

export default [
  watchFetchBox,
  watchFetchBoxes,
  watchCreateBox,
  watchEditBox,
  watchDeleteBox,
];
