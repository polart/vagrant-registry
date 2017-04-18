import React, {Component} from "react";
import Spinner from "react-spinkit";


class MySpinner extends Component {
  render() {
    return (
        <div style={{height: '100%', width: '100%', textAlign: 'center'}}>
          <Spinner spinnerName="three-bounce" />
        </div>
    );
  }
}

export default MySpinner;
