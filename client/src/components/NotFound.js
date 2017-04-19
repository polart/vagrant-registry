import React, {Component} from "react";
import {Link} from "react-router";


class NotFound extends Component {
  render() {
    return (
      <div className="text-center">
        <h1>404 Not Found</h1>
        <h3>That page does not exist</h3>
        <Link to="/">Go Home</Link>
      </div>
    );
  }
}

export default NotFound;
