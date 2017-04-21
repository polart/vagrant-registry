import {call, put, takeLatest} from "redux-saga/effects";
import * as api from "../api";
import {browserHistory} from "react-router";
import * as actionTypes from "../actions/types";
import * as actions from "../actions";
import {callRequest} from './utils';


const fetchUser = callRequest.bind(null, actions.user.fetch, api.fetchUser);
const fetchUsers = callRequest.bind(null, actions.user.fetch, api.fetchUsers);
const editUser = callRequest.bind(null, actions.user.edit, api.editUser);


export function* watchFetchUser() {
  yield takeLatest(actionTypes.LOAD_USER, fetchUser)
}

export function* watchFetchUsers() {
  yield takeLatest(actionTypes.LOAD_USERS, fetchUsers)
}

export function* watchUpdateAccount() {
  yield takeLatest(actionTypes.UPDATE_ACCOUNT, function* ({username, data}) {
    yield put(actions.form.setPending('account', true));
    const { response, error } = yield call(editUser, {username, data});

    if (error) {
      yield put(actions.form.setErrors('account', error));
    } else if (response) {
      yield put(actions.setMyUsername(data.username));
      yield put(actions.form.setMessage('account', 'Changes saved'));
    }
    yield put(actions.form.setPending('account', false));
  });
}

export function* watchChangePassword() {
  yield takeLatest(actionTypes.CHANGE_PASSWORD, function* ({username, data}) {
    let formError;
    if (!data.password.length || !data.password2.length) {
      formError = 'Please enter new password in both fields.'
    } else if (data.password !== data.password2) {
      formError = 'Passwords do not match.'
    }

    if (formError) {
      yield put(actions.form.reset('changePassword'));
      yield put(actions.form.setErrors('changePassword', {detail: formError}));
      return;
    }

    yield put(actions.form.setPending('changePassword', true));
    const { response, error } = yield call(
        editUser,
        {username, data}
    );

    if (error) {
      yield put(actions.form.setErrors('changePassword', error));
      yield put(actions.form.setPending('changePassword', false));
    } else if (response) {
      yield put(actions.form.reset('changePassword'));
      yield put(actions.form.setMessage('changePassword', 'Changes saved'));
    }
  });
}

export function* watchLogin() {
  yield takeLatest(actionTypes.LOGIN, function* ({data}) {
    yield put(actions.form.setPending('login', true));
    const {response, error} = yield call(api.getToken, {data});
    if (response) {
      yield put(actions.setMyUsername(data.username));
      localStorage.token = response.token;
      browserHistory.push('/');
      yield put(actions.form.reset('login'));
    } else if (error) {
      yield put(actions.form.setErrors('login', error));
      yield put(actions.form.setPending('login', false));
    }
  });
}

export function* watchLogout() {
  yield takeLatest(actionTypes.LOGOUT, function* ({nextUrl}) {
    localStorage.removeItem('token');
    localStorage.removeItem('state');
    yield put(actions.setMyUsername(null));
    let url = `/login/`;
    if (nextUrl) {
      url = `/login/?next=${nextUrl}`;
    }
    browserHistory.push(url);
  });
}

export default [
  watchFetchUser,
  watchFetchUsers,
  watchUpdateAccount,
  watchChangePassword,
  watchLogin,
  watchLogout,
];
