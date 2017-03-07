import * as types from './types';


function action(type, payload = {}) {
  return {type, ...payload}
}

export const setMyUsername = (username) => action(types.SET_MY_USERNAME, { username });
