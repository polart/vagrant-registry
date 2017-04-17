import React from "react";
import ReactDOM from "react-dom";
import {Router, Route, browserHistory, IndexRoute} from "react-router";
import {Provider} from "react-redux";
import {createStore, applyMiddleware, compose} from "redux";
import App from "./components/App";
import NotFound from "./components/NotFound";
import BoxListPage from "./components/BoxListPage";
import Login from "./components/Login";
import * as auth from "./auth";
import reducers from "./reducers";
import createSagaMiddleware from "redux-saga";
import rootSaga from "./sagas";
import {loadState, saveState} from "./localStorage";
import {throttle} from "lodash";
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
          <Route path="*" component={NotFound} />
        </Route>
      </Router>
    </Provider>,
    document.getElementById('root')
);
