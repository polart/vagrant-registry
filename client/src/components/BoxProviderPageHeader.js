import React, {Component} from "react";
import {connect} from "react-redux";
import {Label} from "react-bootstrap";
import Moment from "moment";
import * as actions from "../actions";
import {parsePerms} from "../utils";
import ActionIcon from "./ActionIcon";


class BoxProviderPageHeader extends Component {
  onProviderDelete = (e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box provider ${this.props.providerTag}?`)) {
      this.props.deleteBoxProvider(this.props.boxTag, this.props.version, this.props.provider);
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

function mapStateToProps(state, props) {
  const {username, boxName, version, provider} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  const providerTag = `${username}/${boxName} v${version} ${provider}`;
  const boxProvider = state.entities.boxProviders[providerTag];

  return {
    box: state.entities.boxes[boxTag],
    boxTag,
    providerTag,
    version,
    provider,
    boxProvider,
  }
}

export default connect(mapStateToProps, {
  deleteBoxProvider: actions.deleteBoxProvider,
})(BoxProviderPageHeader)
