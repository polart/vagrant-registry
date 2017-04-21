import React from "react";
import ReactDOM from "react-dom";
import {browserHistory, IndexRoute, Redirect, Route, Router} from "react-router";
import {Provider} from "react-redux";
import {applyMiddleware, compose, createStore} from "redux";
import createSagaMiddleware from "redux-saga";
import {throttle} from "lodash";

// Loading global styles before specific styles for components
import "bootstrap/dist/css/bootstrap.css";
import "./styles/bootstrap_custom.css";
import "./styles/common.css";

import * as auth from "./auth";
import reducers from "./reducers";
import rootSaga from "./sagas";
import {loadState, saveState} from "./localStorage";
import App from "./components/App";
import BoxDetail from "./components/BoxDetail";
import BoxVersionDetail from "./components/BoxVersionDetail";
import BoxSearchPage from "./components/BoxSearchPage";
import UserDashPage from "./components/UserDashPage";
import BoxCreatePage from "./components/BoxCreatePage";
import BoxEditPage from "./components/BoxEditPage";
import BoxVersionCreatePage from "./components/BoxVersionCreatePage";
import BoxVersionEditPage from "./components/BoxVersionEditPage";
import BoxProviderCreatePage from "./components/BoxProviderCreatePage";
import BoxProviderEditPage from "./components/BoxProviderEditPage";
import AccountPage from "./components/AccountPage";
import NotFound from "./components/NotFound";
import BoxListPage from "./components/BoxListPage";
import Login from "./components/Login";


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
          <IndexRoute component={UserDashPage} />
          <Route path="/account" component={AccountPage} />
          <Route path="/boxes/search" component={BoxSearchPage} />
          <Route path="/boxes/new" component={BoxCreatePage} />
          <Route path="/boxes(/:username)" component={BoxListPage} />
          <Route path="/boxes/:username/:boxName" component={BoxDetail} />
          <Route path="/boxes/:username/:boxName/edit" component={BoxEditPage} />
          <Route path="/boxes/:username/:boxName/versions" component={BoxDetail} />
          <Route path="/boxes/:username/:boxName/versions/new" component={BoxVersionCreatePage} />
          <Route path="/boxes/:username/:boxName/versions/:version" component={BoxVersionDetail} />
          <Route path="/boxes/:username/:boxName/versions/:version/edit" component={BoxVersionEditPage} />
          <Route path="/boxes/:username/:boxName/versions/:version/providers" component={BoxVersionDetail} />
          <Route path="/boxes/:username/:boxName/versions/:version/providers/new" component={BoxProviderCreatePage} />
          <Route path="/boxes/:username/:boxName/versions/:version/providers/:provider" component={BoxVersionDetail} />
          <Route path="/boxes/:username/:boxName/versions/:version/providers/:provider/edit" component={BoxProviderEditPage} />
          <Redirect from="/:username/:boxName" to="/boxes/:username/:boxName" />
        </Route>
        <Route path="*" component={NotFound} />
      </Router>
    </Provider>,
    document.getElementById('root')
);
