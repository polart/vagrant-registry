import {call, fork, put, race, take, takeLatest} from "redux-saga/effects";
import * as api from "../api";
import {browserHistory} from "react-router";
import * as actionTypes from "../actions/types";
import * as actions from "../actions";
import {getFileMD5Hash} from "../utils";


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
      yield put(actions.logout(location.pathname));
    } else if (status === 404) {
      yield put(actions.setErrorPage(404));
    }
  }
  return { response, error };
}


const fetchUser = callRequest.bind(null, actions.user.fetch, api.fetchUser);
const fetchUsers = callRequest.bind(null, actions.user.fetch, api.fetchUsers);
const editUser = callRequest.bind(null, actions.user.edit, api.editUser);

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

function* uploadChunks({file, offset, tag, version, provider, upload}) {
  const totalSize = file.size;
  const chunkSize = 5242880;  // 5MB
  let numberOfErrors = 0;
  let loaded = offset;

  let data;
  let dataSize;
  let resp;
  while (loaded < totalSize) {
    data = file.slice(loaded, loaded + chunkSize);
    dataSize = data.size;
    resp = yield call(api.uploadBoxChunk, {
      tag,
      version,
      provider,
      upload,
      data: data,
      range: {
        start: loaded,
        end: loaded + dataSize - 1,
        total: totalSize,
      }
    });

    if (resp.response) {
      numberOfErrors = 0;
      loaded += dataSize;
      yield put(actions.form.updateData(
          'boxProvider',
          { uploadProgress: {loaded, totalSize} }
      ));
    } else if (resp.error) {
      numberOfErrors += 1;

      if (numberOfErrors >= 3) {
        throw new Error(resp.error);
      }

      if (resp.status === 415) {
        loaded = resp.error.offset;
      }

      throw new Error(resp.error);
    }
  }
}

function* uploadBoxFile({tag, version, provider, data}) {
  yield put(actions.form.updateData(
      'boxProvider',
      { uploadStatus: 'Computing file hash...' }
  ));

  const hash = yield call(getFileMD5Hash, data.file);
  yield put(actions.form.updateData(
      'boxProvider',
      { uploadStatus: 'Uploading box...' }
  ));

  let boxUploadResp = yield call(
      api.fetchBoxUpload,
      {tag, version, provider, upload: hash}
  );

  if (boxUploadResp.status === 404) {
    const uploadData = {
      checksum: hash,
      file_size: data.file.size,
      checksum_type: 'md5',
    };
    boxUploadResp = yield call(
        api.createBoxUpload,
        {tag, version, provider, data: uploadData}
    );
  }

  if (boxUploadResp.error) {
    yield put(actions.form.setErrors('boxProvider', boxUploadResp.error));
    yield put(actions.form.setPending('boxProvider', false));
    yield put(actions.form.updateData(
        'boxProvider',
        { uploadStatus: null }
    ));
    return
  }

  try {
    yield call(uploadChunks, {
      tag,
      version,
      provider,
      upload: hash,
      file: data.file,
      offset: boxUploadResp.response.offset,
    });
  } catch (error) {
    yield put(actions.form.setErrors('boxProvider', error));
    yield put(actions.form.setPending('boxProvider', false));
    yield put(actions.form.updateData(
        'boxProvider',
        { uploadStatus: null }
    ));
    return;
  }

  yield put(actions.form.reset('boxProvider'));
  browserHistory.push(`/boxes/${tag}/versions/${version}/`);
}

export function* watchCreateBoxProvider() {
  yield takeLatest(actionTypes.CREATE_BOX_PROVIDER, function* ({tag, version, data}) {
    yield put(actions.form.setPending('boxProvider', true));
    const { response, error } = yield call(createBoxProvider, {tag, version, data});

    if (error) {
      yield put(actions.form.setErrors('boxProvider', error));
      yield put(actions.form.setPending('boxProvider', false));
    } else if (response) {
      if (data.file) {
        yield call(uploadBoxFile, {tag, version, provider: data.provider, data});
      } else {
        yield put(actions.form.reset('boxProvider'));
        browserHistory.push(`/boxes/${tag}/versions/${version}/`);
      }
    }
  });
}

export function* watchEditBoxProvider() {
  yield takeLatest(actionTypes.EDIT_BOX_PROVIDER, function* ({tag, version, provider, data}) {
    yield put(actions.form.setPending('boxProvider', true));
    const { response, error } = yield call(editBoxProvider, {tag, version, provider, data});

    if (error) {
      yield put(actions.form.setErrors('boxProvider', error));
      yield put(actions.form.setPending('boxProvider', false));
    } else if (response) {
      if (data.file) {
        yield call(uploadBoxFile, {tag, version, provider, data});
      } else {
        yield put(actions.form.reset('boxProvider'));
        browserHistory.push(`/boxes/${tag}/versions/${version}/`);
      }
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
    watchUpdateAccount(),
    watchChangePassword(),

    watchLogout(),
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
