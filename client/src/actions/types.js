function createRequestTypes(base) {
  return ['REQUEST', 'SUCCESS', 'FAILURE'].reduce((reqAcc, type) => {
    reqAcc[type] = `${base}_${type}`;
    return reqAcc
  }, {});
}

export const SET_ERROR_PAGE = 'SET_ERROR_PAGE';
export const CLEAR_ERROR_PAGE = 'CLEAR_ERROR_PAGE';

export const LOAD_USER = 'LOAD_USER';
export const LOAD_USERS = 'LOAD_USERS';

export const UPDATE_ACCOUNT = 'UPDATE_ACCOUNT';
export const CHANGE_PASSWORD = 'CHANGE_PASSWORD';

export const USER = {
  FETCH: createRequestTypes('USER_FETCH'),
  EDIT: createRequestTypes('USER_EDIT'),
};


export const LOAD_BOX = 'LOAD_BOX';
export const CREATE_BOX = 'CREATE_BOX';
export const EDIT_BOX = 'EDIT_BOX';
export const DELETE_BOX = 'DELETE_BOX';
export const LOAD_BOXES = 'LOAD_BOXES';

export const LOAD_BOX_VERSION = 'LOAD_BOX_VERSION';
export const LOAD_BOX_VERSIONS = 'LOAD_BOX_VERSIONS';
export const CREATE_BOX_VERSION = 'CREATE_BOX_VERSION';
export const EDIT_BOX_VERSION = 'EDIT_BOX_VERSION';
export const DELETE_BOX_VERSION = 'DELETE_BOX_VERSION';

export const CREATE_BOX_PROVIDER = 'CREATE_BOX_PROVIDER';
export const EDIT_BOX_PROVIDER = 'EDIT_BOX_PROVIDER';
export const DELETE_BOX_PROVIDER = 'DELETE_BOX_PROVIDER';

export const BOX = {
  FETCH: createRequestTypes('BOX_FETCH'),
  CREATE: createRequestTypes('BOX_CREATE'),
  EDIT: createRequestTypes('BOX_EDIT'),
  DELETE: createRequestTypes('BOX_DELETE'),
};

export const BOX_VERSION = {
  FETCH: createRequestTypes('BOX_VERSION_FETCH'),
  CREATE: createRequestTypes('BOX_VERSION_CREATE'),
  EDIT: createRequestTypes('BOX_VERSION_EDIT'),
  DELETE: createRequestTypes('BOX_VERSION_DELETE'),
};

export const BOX_PROVIDER = {
  CREATE: createRequestTypes('BOX_PROVIDER_CREATE'),
  EDIT: createRequestTypes('BOX_PROVIDER_EDIT'),
  DELETE: createRequestTypes('BOX_PROVIDER_DELETE'),
};

export const SET_MY_USERNAME = 'SET_MY_USERNAME';
export const LOGOUT = 'LOGOUT';
export const LOGIN = 'LOGIN';

export const FORM = {
  SET_PENDING: 'FORM_SET_PENDING',
  SET_DATA: 'FORM_SET_DATA',
  SET_MESSAGE: 'FORM_SET_MESSAGE',
  UPDATE_DATA: 'FORM_UPDATE_DATA',
  FIELD_CHANGE: 'FORM_FIELD_CHANGE',
  SET_ERRORS: 'FORM_SET_ERRORS',
  CLEAR_ERRORS: 'FORM_CLEAR_ERRORS',
  RESET: 'FORM_RESET',
};
