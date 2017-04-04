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


export const LOAD_BOXES = 'LOAD_BOXES';

export const BOX = {
  FETCH: createRequestTypes('BOX_FETCH'),
};

export const SET_MY_USERNAME = 'SET_MY_USERNAME';
