import {call, put} from "redux-saga/effects";
import * as actions from "../actions";


export function* callRequest(entity, apiFn, data = null) {
  yield put(entity.request(data));
  const {response, error, status} = yield call(apiFn, data);
  if (response) {
    yield put(entity.success(data, response));
  }
  else {
    yield put(entity.failure(data, error));
    if (status === 401) {
      yield put(actions.logout(window.location.pathname));
    } else if (status === 404) {
      yield put(actions.setErrorPage(404));
    }
  }
  return {response, error};
}
