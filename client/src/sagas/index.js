import { fork } from 'redux-saga/effects';
import usersSagas from './users';
import boxesSagas from './boxes';
import boxVersionsSagas from './boxVersions';
import boxProvidersSagas from './boxProviders';

const sagas = [
  ...usersSagas,
  ...boxesSagas,
  ...boxVersionsSagas,
  ...boxProvidersSagas,
];


export default function* rootSaga() {
  yield sagas.map(saga => fork(saga));
}
