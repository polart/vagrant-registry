import * as types from './types';


function action(type, payload = {}) {
  // Order matters. `type` should be at the end,
  // so it will override any type in payload.
  return {...payload, type}
}

export const setMyUsername = (username) => action(types.SET_MY_USERNAME, { username });
export const loadUser = (username) => action(types.LOAD_USER, { username });
export const loadUsers = () => action(types.LOAD_USERS);

export const loadBox = (tag = null) => action(types.LOAD_BOX, { tag });
export const loadBoxes = (username = null, page = null, ordering = null, search = null) => {
  return action(types.LOAD_BOXES, { username, page, ordering, search });
};
export const createBox = (username, data) => action(types.CREATE_BOX, { username, data });
export const editBox = (tag, data) => action(types.EDIT_BOX, { tag, data });
export const deleteBox = (tag) => action(types.DELETE_BOX, { tag });

export const loadBoxVersion = (tag = null, version = null) => action(types.LOAD_BOX_VERSION, { tag, version });
export const loadBoxVersions = (tag = null, page = null) => action(types.LOAD_BOX_VERSIONS, { tag, page });
export const createBoxVersion = (tag, data) => action(
    types.CREATE_BOX_VERSION,
    { tag, data }
);
export const editBoxVersion = (tag, version, data) => action(
    types.EDIT_BOX_VERSION,
    { tag, version, data }
);
export const deleteBoxVersion = (tag, version) => action(
    types.DELETE_BOX_VERSION,
    { tag, version }
);

export const createBoxProvider = (tag, version, data) => action(
    types.CREATE_BOX_PROVIDER,
    { tag, version, data }
);
export const editBoxProvider = (tag, version, provider, data) => action(
    types.EDIT_BOX_PROVIDER,
    { tag, version, provider, data }
);
export const deleteBoxProvider = (tag, version, provider) => action(
    types.DELETE_BOX_PROVIDER,
    { tag, version, provider }
);

export const user = {
  fetch: {
    request: ({ username}) => action(types.USER.FETCH.REQUEST, {username}),
    success: (_, response) => action(types.USER.FETCH.SUCCESS, {response}),
    failure: (_, error) => action(types.USER.FETCH.FAILURE, {error}),
  },
};

export const box = {
  fetch: {
    request: (data) => action(types.BOX.FETCH.REQUEST, data),
    success: (data, response) => action(types.BOX.FETCH.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX.FETCH.FAILURE, { ...data, error }),
  },
  create: {
    request: (data) => action(types.BOX.CREATE.REQUEST, data),
    success: (data, response) => action(types.BOX.CREATE.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX.CREATE.FAILURE, { ...data, error }),
  },
  edit: {
    request: (data) => action(types.BOX.EDIT.REQUEST, data),
    success: (data, response) => action(types.BOX.EDIT.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX.EDIT.FAILURE, { ...data, error }),
  },
  delete: {
    request: (data) => action(types.BOX.DELETE.REQUEST, data),
    success: (data, response) => action(types.BOX.DELETE.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX.DELETE.FAILURE, { ...data, error }),
  },
};

export const boxVersion = {
  fetch: {
    request: ({ tag }) => action(types.BOX_VERSION.FETCH.REQUEST, {tag}),
    success: ({ tag }, response) => action(types.BOX_VERSION.FETCH.SUCCESS, {tag, response}),
    failure: ({ tag }, error) => action(types.BOX_VERSION.FETCH.FAILURE, {tag, error}),
  },
  create: {
    request: (data) => action(types.BOX_VERSION.CREATE.REQUEST, data),
    success: (data, response) => action(types.BOX_VERSION.CREATE.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX_VERSION.CREATE.FAILURE, { ...data, error }),
  },
  edit: {
    request: (data) => action(types.BOX_VERSION.EDIT.REQUEST, data),
    success: (data, response) => action(types.BOX_VERSION.EDIT.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX_VERSION.EDIT.FAILURE, { ...data, error }),
  },
  delete: {
    request: (data) => action(types.BOX_VERSION.DELETE.REQUEST, data),
    success: (data, response) => action(types.BOX_VERSION.DELETE.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX_VERSION.DELETE.FAILURE, { ...data, error }),
  },
};

export const boxProvider = {
  create: {
    request: (data) => action(types.BOX_PROVIDER.CREATE.REQUEST, data),
    success: (data, response) => action(types.BOX_PROVIDER.CREATE.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX_PROVIDER.CREATE.FAILURE, { ...data, error }),
  },
  edit: {
    request: (data) => action(types.BOX_PROVIDER.EDIT.REQUEST, data),
    success: (data, response) => action(types.BOX_PROVIDER.EDIT.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX_PROVIDER.EDIT.FAILURE, { ...data, error }),
  },
  delete: {
    request: (data) => action(types.BOX_PROVIDER.DELETE.REQUEST, data),
    success: (data, response) => action(types.BOX_PROVIDER.DELETE.SUCCESS, { ...data, response }),
    failure: (data, error) => action(types.BOX_PROVIDER.DELETE.FAILURE, { ...data, error }),
  },
};

export const form = {
  setPending: (model, pending) => action(types.FORM.SET_PENDING, {model, pending}),
  setData: (model, data) => action(types.FORM.SET_DATA, {model, data}),
  updateData: (model, data) => action(types.FORM.UPDATE_DATA, {model, data}),
  fieldChange: (model, value) => action(types.FORM.FIELD_CHANGE, {model, value}),
  setErrors: (model, errors) => action(types.FORM.SET_ERRORS, {model, errors}),
  clearErrors: (model) => action(types.FORM.CLEAR_ERRORS, {model}),
  reset: (model) => action(types.FORM.RESET, {model}),
};
