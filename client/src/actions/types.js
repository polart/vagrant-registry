function createRequestTypes(base) {
  return ['REQUEST', 'SUCCESS', 'FAILURE'].reduce((reqAcc, type) => {
    reqAcc[type] = `${base}_${type}`;
    return reqAcc
  }, {});
}

export const LOAD_USER = 'LOAD_USER';
export const LOAD_USERS = 'LOAD_USERS';


export const USER = {
  FETCH: createRequestTypes('USER_FETCH'),
};


export const LOAD_BOX = 'LOAD_BOX';
export const CREATE_BOX = 'CREATE_BOX';
export const EDIT_BOX = 'EDIT_BOX';
export const DELETE_BOX = 'DELETE_BOX';
export const LOAD_BOXES = 'LOAD_BOXES';
export const LOAD_BOX_VERSION = 'LOAD_BOX_VERSION';
export const LOAD_BOX_VERSIONS = 'LOAD_BOX_VERSIONS';

export const BOX = {
  FETCH: createRequestTypes('BOX_FETCH'),
  CREATE: createRequestTypes('BOX_CREATE'),
  EDIT: createRequestTypes('BOX_EDIT'),
  DELETE: createRequestTypes('BOX_DELETE'),
};

export const BOX_VERSION = {
  FETCH: createRequestTypes('BOX_VERSION_FETCH'),
};

export const SET_MY_USERNAME = 'SET_MY_USERNAME';

export const FORM = {
  SET_PENDING: 'FORM_SET_PENDING',
  SET_DATA: 'FORM_SET_DATA',
  FIELD_CHANGE: 'FORM_FIELD_CHANGE',
  SET_ERRORS: 'FORM_SET_ERRORS',
  CLEAR_ERRORS: 'FORM_CLEAR_ERRORS',
  RESET: 'FORM_RESET',
};
