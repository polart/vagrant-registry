import React, {Component} from "react";
import {connect} from "react-redux";
import Login from "./Login";
import MyNavbar from "./MyNavbar";
import * as actions from '../actions';


class App extends Component {
  componentDidMount() {
    if (this.props.myUsername) {
      this.props.loadUser(this.props.myUsername);
    }
  }

  render() {
    if (this.props.location.pathname === '/' && !this.props.myUsername) {
      return <Login router={this.props.router} />;
    }

    return (
        <div>
          <MyNavbar
              username={this.props.myUsername}
              isStaff={this.props.isStaff}
              onLogout={this.props.logout}
              router={this.props.router}
          />
          <div style={{marginTop: '60px'}}>
            {this.props.children}
          </div>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const myUsername = state.myUsername;
  let user;
  if (myUsername) {
    user = state.entities.users[myUsername];
  }
  const isStaff = user && user.is_staff;
  return {
    myUsername,
    user,
    isStaff,
  }
}

export default connect(mapStateToProps, {
  loadUser: actions.loadUser,
  logout: actions.logout,
})(App)
