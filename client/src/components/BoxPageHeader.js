import React, {Component} from "react";
import {connect} from "react-redux";
import {Badge, Label} from "react-bootstrap";
import Moment from "moment";
import PropTypes from 'prop-types';
import * as actions from "../actions";
import {parsePerms} from "../utils";
import ActionIcon from "./ActionIcon";
import {getBox, getBoxTag} from "../selectors";


class BoxPageHeader extends Component {
  onBoxEdit = (e) => {
    this.props.router.push(
        `/boxes/${this.props.boxTag}/edit/`
    );
  };

  onBoxDelete = (e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box ${this.props.boxTag}?`)) {
      this.props.deleteBox(this.props.boxTag);
    }
  };

  renderPrivateLabel = () => {
    if (!this.props.box) {
      return null;
    }
    if (this.props.box.visibility === 'PT') {
      return <Label className="label-private">Private</Label>;
    }
    return null;
  };

  renderEditBoxIcon = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canEdit) {
      return <ActionIcon icon="edit" title="Edit box" onClick={this.onBoxEdit} />;
    }
    return null;
  };

  renderDeleteBoxIcon = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canDelete) {
      return <ActionIcon icon="trash" title="Delete box" onClick={this.onBoxDelete} />;
    }
    return null;
  };

  renderLastUpdated = () => {
    if (!this.props.box) {
      return null;
    }
    return (
        <span title={Moment(this.props.box.date_updated).format('LLL')}>
          Last updated: {Moment(this.props.box.date_updated).fromNow()}
        </span>
    );
  };

  renderPulls = () => {
    if (!this.props.box) {
      return null;
    }
    return (
        <span>
          {' | '}<Badge>{this.props.box.pulls}</Badge> pulls
        </span>
    );
  };

  render() {
    return (
        <div className="page-header">
          <h1>
            <span>{this.props.boxTag}</span>
            {' '}
            {this.renderPrivateLabel()}
            {' '}
            {this.renderEditBoxIcon()}
            {this.renderDeleteBoxIcon()}
          </h1>
          <div className="page-header-subtitle">
            {this.renderLastUpdated()}
            {this.renderPulls()}
          </div>
        </div>
    );
  }
}

BoxPageHeader.propTypes = {
  router: PropTypes.object.isRequired,
};

function mapStateToProps(state, props) {
  return {
    box: getBox(state, props),
    boxTag: getBoxTag(props),
  }
}

export default connect(mapStateToProps, {
  deleteBox: actions.deleteBox,
})(BoxPageHeader)
