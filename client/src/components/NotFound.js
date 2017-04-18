import React, {Component} from "react";
import {Link} from "react-router";


class NotFound extends Component {
  render() {
    return (
      <div>
        <p>404 Not Found</p>
        <Link to="/">Go Home</Link>
      </div>
    );
  }
}

export default NotFound;
