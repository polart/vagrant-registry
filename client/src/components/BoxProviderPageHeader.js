import React, {Component} from "react";
import {connect} from "react-redux";
import {Label} from "react-bootstrap";
import Moment from "moment";
import PropTypes from 'prop-types';
import * as actions from "../actions";
import {parsePerms} from "../utils";
import ActionIcon from "./ActionIcon";
import {getBoxProvider, getBoxProviderTag, getBoxTag, getBox} from "../selectors";


class BoxProviderPageHeader extends Component {
  onProviderDelete = (e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box provider ${this.props.providerTag}?`)) {
      this.props.deleteBoxProvider(
          this.props.boxTag,
          this.props.router.params.version,
          this.props.router.params.provider
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

  renderDeleteProviderIcon = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canDelete) {
      return <ActionIcon icon="trash" title="Delete box" onClick={this.onProviderDelete} />;
    }
    return null;
  };

  renderLastUpdated = () => {
    if (!this.props.boxProvider) {
      return null;
    }
    return (
        <span title={Moment(this.props.boxProvider.date_updated).format('LLL')}>
          Last updated: {Moment(this.props.boxProvider.date_updated).fromNow()}
        </span>
    );
  };

  render() {
    return (
        <div className="page-header">
          <h1>
            <span>{this.props.providerTag}</span>
            {' '}
            {this.renderPrivateLabel()}
            {' '}
            {this.renderDeleteProviderIcon()}
          </h1>
          <div className="page-header-subtitle">
            {this.renderLastUpdated()}
          </div>
        </div>
    );
  }
}

BoxProviderPageHeader.propTypes = {
  router: PropTypes.object.isRequired,
};

function mapStateToProps(state, props) {
  return {
    box: getBox(state, props),
    boxTag: getBoxTag(props),
    providerTag: getBoxProviderTag(props),
    boxProvider: getBoxProvider(state, props),
  }
}

export default connect(mapStateToProps, {
  deleteBoxProvider: actions.deleteBoxProvider,
})(BoxProviderPageHeader)
