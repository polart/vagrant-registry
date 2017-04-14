import React, {Component} from "react";
import {connect} from "react-redux";
import Login from "./Login";
import MyNavbar from "./MyNavbar";


class App extends Component {
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
})(App)
