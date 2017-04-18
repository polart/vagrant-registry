import React, {Component} from "react";
import {Button} from "react-bootstrap";


class MySubmitButton extends Component {
  render() {
    let title = this.props.title;
    if (this.props.pending && this.props.pendingTitle) {
      title = this.props.pendingTitle;
    }
    return (
        <Button
            bsStyle="success"
            type="submit"
            disabled={this.props.pending}
        >
          {title}
        </Button>
    );
  }
}

export default MySubmitButton;
