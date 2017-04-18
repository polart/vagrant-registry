import React, {Component} from "react";
import {connect} from "react-redux";
import Login from "./Login";
import MyNavbar from "./MyNavbar";
import * as actions from '../actions';
import NotFound from "./NotFound";


class App extends Component {
  componentDidMount() {
    this.props.router.listenBefore(this.beforeRouterChange.bind(this));
    if (this.props.myUsername) {
      this.props.loadUser(this.props.myUsername);
    }
  }

  beforeRouterChange() {
    if (this.props.errorPage) {
      this.props.clearErrorPage();
    }
  }

  render() {
    if (this.props.location.pathname === '/' && !this.props.myUsername) {
      return <Login router={this.props.router} />;
    }

    if (this.props.errorPage === 404) {
      return <NotFound />
    }

    return (
        <div>
          <MyNavbar
              username={this.props.myUsername}
              isStaff={this.props.isStaff}
              onLogout={this.props.logout}
              router={this.props.router}
          />
          <div className="container">
            {this.props.children}
          </div>
        </div>
    );
  }
}

function mapStateToProps(state) {
  const myUsername = state.myUsername;
  let user;
  if (myUsername) {
    user = state.entities.users[myUsername];
  }
  const isStaff = user && user.is_staff;
  return {
    errorPage: state.errorPage,
    myUsername,
    user,
    isStaff,
  }
}

export default connect(mapStateToProps, {
  loadUser: actions.loadUser,
  logout: actions.logout,
  clearErrorPage: actions.clearErrorPage,
})(App)
