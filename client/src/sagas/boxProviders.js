import {call, put, takeLatest} from "redux-saga/effects";
import * as api from "../api";
import {browserHistory} from "react-router";
import * as actionTypes from "../actions/types";
import * as actions from "../actions";
import {callRequest} from "./utils";
import {getFileMD5Hash} from "../utils";


const createBoxProvider = callRequest.bind(null, actions.boxProvider.create, api.createBoxProvider);
const editBoxProvider = callRequest.bind(null, actions.boxProvider.edit, api.editBoxProvider);
const deleteBoxProvider = callRequest.bind(null, actions.boxProvider.delete, api.deleteBoxProvider);


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
    const { response } = yield call(deleteBoxProvider, {tag, version, provider});

    if (response) {
      yield put(actions.loadBoxVersion(tag, version));
      browserHistory.push(`/boxes/${tag}/versions/${version}/`);
    }
  });
}

export default [
  watchCreateBoxProvider,
  watchEditBoxProvider,
  watchDeleteBoxProvider,
];
