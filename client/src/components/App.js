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
          <MyNavbar router={this.props.router} />
          <div style={{marginTop: '60px'}}>
            {this.props.children}
          </div>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    myUsername: state.myUsername,
  }
}

export default connect(mapStateToProps, {
  loadUser: actions.loadUser,
})(App)
