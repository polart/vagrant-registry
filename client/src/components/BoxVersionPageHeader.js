import React, {Component} from "react";
import {connect} from "react-redux";
import {Label} from "react-bootstrap";
import Moment from "moment";
import PropTypes from 'prop-types';
import * as actions from "../actions";
import {parsePerms} from "../utils";
import ActionIcon from "./ActionIcon";
import {getBox, getBoxTag, getBoxVersionTag} from "../selectors";


class BoxVersionPageHeader extends Component {
  onBoxVersionEdit = (e) => {
    this.props.router.push(
        `/boxes/${this.props.boxTag}/versions/${this.props.params.version}/edit/`
    );
  };

  onBoxVersionDelete = (e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box version ${this.props.versionTag}?`)) {
      this.props.deleteBoxVersion(
          this.props.boxTag,
          this.props.params.version
      );
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

  renderEditVersionIcon = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canEdit) {
      return <ActionIcon icon="edit" title="Edit version" onClick={this.onBoxVersionEdit} />;
    }
    return null;
  };

  renderDeleteVersionIcon = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canDelete) {
      return <ActionIcon icon="trash" title="Delete version" onClick={this.onBoxVersionDelete} />;
    }
    return null;
  };

  renderLastUpdated = () => {
    if (!this.props.boxVersion) {
      return null;
    }
    return (
        <span title={Moment(this.props.boxVersion.date_updated).format('LLL')}>
          Last updated: {Moment(this.props.boxVersion.date_updated).fromNow()}
        </span>
    );
  };

  render() {
    return (
        <div className="page-header">
          <h1>
            <span>{this.props.versionTag}</span>
            {' '}
            {this.renderPrivateLabel()}
            {' '}
            {this.renderEditVersionIcon()}
            {this.renderDeleteVersionIcon()}
          </h1>
          <div className="page-header-subtitle">
            {this.renderLastUpdated()}
          </div>
        </div>
    );
  }
}

BoxVersionPageHeader.propTypes = {
  router: PropTypes.object.isRequired,
};

function mapStateToProps(state, props) {
  return {
    box: getBox(state, props),
    boxTag: getBoxTag(props),
    versionTag: getBoxVersionTag(props),
  }
}

export default connect(mapStateToProps, {
  deleteBoxVersion: actions.deleteBoxVersion,
})(BoxVersionPageHeader)
