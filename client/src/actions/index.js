import * as types from './types';


function action(type, payload = {}) {
  return {type, ...payload}
}

export const setMyUsername = (username) => action(types.SET_MY_USERNAME, { username });
export const loadUser = (username) => action(types.LOAD_USER, { username });
export const loadUsers = () => action(types.LOAD_USERS);

export const loadBox = (tag = null) => action(types.LOAD_BOX, { tag });
export const loadBoxes = (username = null, page = null) => action(types.LOAD_BOXES, { username, page });

export const loadBoxVersions = (tag = null, page = null) => action(types.LOAD_BOX_VERSIONS, { tag, page });

export const user = {
  fetch: {
    request: ({ username}) => action(types.USER.FETCH.REQUEST, {username}),
    success: (_, response) => action(types.USER.FETCH.SUCCESS, {response}),
    failure: (_, error) => action(types.USER.FETCH.FAILURE, {error}),
  },
};

export const box = {
  fetch: {
    request: ({ username}) => action(types.BOX.FETCH.REQUEST, {username}),
    success: (_, response) => action(types.BOX.FETCH.SUCCESS, {response}),
    failure: (_, error) => action(types.BOX.FETCH.FAILURE, {error}),
  },
};

export const boxVersion = {
  fetch: {
    request: ({ tag }) => action(types.BOX_VERSION.FETCH.REQUEST, {tag}),
    success: ({ tag }, response) => action(types.BOX_VERSION.FETCH.SUCCESS, {tag, response}),
    failure: ({ tag }, error) => action(types.BOX_VERSION.FETCH.FAILURE, {tag, error}),
  },
};
