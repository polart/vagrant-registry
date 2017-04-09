import React from "react";
import ReactDOM from "react-dom";
import { Router, Route, browserHistory } from "react-router";
import {Provider} from "react-redux";
import {createStore, applyMiddleware, compose} from "redux";
import App from "./components/App";
import NotFound from "./components/NotFound";
import BoxList from "./components/BoxList";
import Login from "./components/Login";
import * as auth from "./auth";
import reducers from "./reducers";
import createSagaMiddleware from "redux-saga";
import rootSaga from "./sagas";
import {loadState, saveState} from "./localStorage";
import {throttle} from "lodash";
import BoxDetail from "./components/BoxDetail";
import BoxVersionDetail from "./components/BoxVersionDetail";


const persistedSate = loadState();
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
const sagaMiddleware = createSagaMiddleware();
const store = createStore(
    reducers,
    persistedSate,
    composeEnhancers(
        applyMiddleware(sagaMiddleware)
    ),
);

store.subscribe(throttle(() => {
  const state = store.getState();
  saveState({
    myUsername: state.myUsername,
  });
}, 1000));

sagaMiddleware.run(rootSaga);


function requireAnon(nextState, replace) {
  if (auth.loggedIn()) {
    replace({
      pathname: '/',
    })
  }
}

ReactDOM.render(
    <Provider store={store}>
      <Router history={browserHistory}>
        <Route path="/login" component={Login} onEnter={requireAnon} />
        <Route path="/" component={App}>
          <Route path="/boxes(/:username)" component={BoxList} />
          <Route path="/boxes/:username/:boxName" component={BoxDetail} />
          <Route path="/boxes/:username/:boxName/versions/:version" component={BoxVersionDetail} />
          <Route path="*" component={NotFound} />
        </Route>
      </Router>
    </Provider>,
    document.getElementById('root')
);
