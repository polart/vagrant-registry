import React, {Component} from "react";
import { connect } from 'react-redux';
import {PageHeader, Panel } from 'react-bootstrap';
import Moment from 'moment';
import {isEmpty} from 'lodash';
import * as actions from "../actions";
import BoxProviderList from "./BoxProviderList";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {Link} from "react-router";
import {parsePerms} from "../utils";
import MySpinner from "./MySpinner";


class BoxVersionDetail extends Component {
  componentDidMount() {
    this.props.fetchBox(this.props.boxTag);
    this.props.fetchBoxVersion(this.props.boxTag, this.props.params.version);
  }

  renderEditOption = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canEdit) {
      return <Link to={`/boxes/${this.props.boxTag}/versions/${this.props.version}/edit/`}>Edit</Link>;
    }
    return null;
  };

  onBoxVersionDelete = (e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box version ${this.props.versionTag}?`)) {
      this.props.deleteBoxVersion(this.props.boxTag, this.props.version);
    }
  };

  renderDeleteOption = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canDelete) {
      return <a href="#" onClick={this.onBoxVersionDelete}>Delete</a>;
    }
    return null;
  };

  onBoxProviderDelete = (provider, e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box provider ${this.props.versionTag} ${provider}?`)) {
      this.props.deleteBoxProvider(this.props.boxTag, this.props.version, provider);
    }
  };

  canDeleteProvider = () => {
    if (!this.props.box) {
      return false;
    }
    return parsePerms(this.props.box.user_permissions).canDelete;
  };

  canEditProvider = () => {
    if (!this.props.box) {
      return false;
    }
    return parsePerms(this.props.box.user_permissions).canEdit;
  };

  renderNewProviderButton = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canPush) {
      return (
          <Link to={`/boxes/${this.props.boxTag}/versions/${this.props.version}/providers/new/`}
                className='btn btn-success'>
          New provider
          </Link>
      );
    }
    return null;
  };

  renderDetails = () => {
    if (!this.props.boxVersion) {
      return <MySpinner />;
    }

    return (
      <div>
        {this.renderEditOption()}
        {' '}
        {this.renderDeleteOption()}
        <p title={Moment(this.props.boxVersion.date_updated).format('LLL')}>
          Last updated: {Moment(this.props.boxVersion.date_updated).fromNow()}
        </p>
        {!isEmpty(this.props.boxVersion.changes) &&
          <Panel header="Changes">
            {this.props.boxVersion.changes}
          </Panel>
        }
        {this.renderNewProviderButton()}
        <BoxProviderList
            boxTag={this.props.boxTag}
            version={this.props.version}
            providers={this.props.boxProviders}
            onDelete={this.onBoxProviderDelete}
            canDelete={this.canDeleteProvider()}
            canEdit={this.canEditProvider()}
        />
      </div>
    );
  };

  render() {
    return (
        <div>
          <PageHeader>{this.props.versionTag}</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          {this.renderDetails()}
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName, version} = props.params;
  const boxTag = `${username}/${boxName}`;
  const versionTag = `${username}/${boxName} v${version}`;
  const boxVersion = state.entities.boxVersions[versionTag];

  let boxProviders;
  if (boxVersion && boxVersion.providers) {
    boxProviders = boxVersion.providers.map(p => state.entities.boxProviders[p]);
  }
  return {
    box: state.entities.boxes[boxTag],
    boxVersion,
    boxProviders,
    boxTag,
    versionTag,
    version,
  }
}

export default connect(mapStateToProps, {
  fetchBox: actions.loadBox,
  fetchBoxVersion: actions.loadBoxVersion,
  deleteBoxVersion: actions.deleteBoxVersion,
  deleteBoxProvider: actions.deleteBoxProvider,
})(BoxVersionDetail)
