import React, {Component} from "react";
import {Glyphicon} from "react-bootstrap";


class ActionIcon extends Component {
  render() {
    return (
        <Glyphicon
            glyph={this.props.icon}
            className="action-icon"
            title={this.props.title}
            onClick={this.props.onClick}
        />
    );
  }
}

export default ActionIcon;
