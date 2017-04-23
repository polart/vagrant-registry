import React, {Component} from "react";
import {connect} from "react-redux";
import {Panel} from "react-bootstrap";
import {isEmpty} from "lodash";
import ReactMarkdown from "react-markdown";
import * as actions from "../actions";
import BoxProviderList from "./BoxProviderList";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {parsePerms} from "../utils";
import MySpinner from "./MySpinner";
import BoxVersionPageHeader from "./BoxVersionPageHeader";
import {getBox, getBoxTag, getBoxVersion, getBoxVersionTag, getBoxProviders} from "../selectors";

import '../styles/BoxVersionDetailPage.css';


class BoxVersionDetailPage extends Component {
  componentDidMount() {
    this.props.fetchBox(this.props.boxTag);
    this.props.fetchBoxVersion(this.props.boxTag, this.props.params.version);
  }

  onBoxProviderDelete = (provider, e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box provider ${this.props.versionTag} ${provider}?`)) {
      this.props.deleteBoxProvider(this.props.boxTag, this.props.version, provider);
    }
  };

  onBoxProviderEdit = (provider, e) => {
    e.preventDefault();
    this.props.router.push(
        `/boxes/${this.props.boxTag}/versions/${this.props.params.version}/providers/${provider}/edit/`
    );
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

  canCreateProvider = () => {
    if (!this.props.box) {
      return false;
    }
    return parsePerms(this.props.box.user_permissions).canPush;
  };

  renderDetails = () => {
    if (!this.props.boxVersion) {
      return <MySpinner />;
    }

    return (
      <div>
        {!isEmpty(this.props.boxVersion.changes) &&
          <Panel header="Changes">
            <ReactMarkdown source={this.props.boxVersion.changes} />
          </Panel>
        }
        <Panel header="Providers" className="box-version-providers-panel">
          <BoxProviderList
              boxTag={this.props.boxTag}
              version={this.props.params.version}
              providers={this.props.boxProviders}
              canDelete={this.canDeleteProvider()}
              canEdit={this.canEditProvider()}
              canCreate={this.canCreateProvider()}
              onDelete={this.onBoxProviderDelete}
              onEdit={this.onBoxProviderEdit}
          />
        </Panel>
      </div>
    );
  };

  render() {
    return (
        <div>
          <BoxVersionPageHeader router={this.props.router} />
          <MyBreadcrumbs router={this.props.router} />
          {this.renderDetails()}
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    box: getBox(state, props),
    boxTag: getBoxTag(props),
    boxVersion: getBoxVersion(state, props),
    versionTag: getBoxVersionTag(props),
    boxProviders: getBoxProviders(state, props),
  }
}

export default connect(mapStateToProps, {
  fetchBox: actions.loadBox,
  fetchBoxVersion: actions.loadBoxVersion,
  deleteBoxVersion: actions.deleteBoxVersion,
  deleteBoxProvider: actions.deleteBoxProvider,
})(BoxVersionDetailPage)
