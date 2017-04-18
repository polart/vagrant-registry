import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";
import BoxVersionForm from "./BoxVersionForm";
import {isEqual} from "lodash";


class BoxVersionEditPage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
      return;
    }
    if (!this.props.boxVersion) {
      this.props.fetchBoxVersion(this.props.boxTag, this.props.version);
      return;
    }
    this.props.setFormData('boxVersion', this.props.boxVersion);
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.boxVersion, this.props.boxVersion)) {
      // For a case when user data loaded
      this.props.setFormData('boxVersion', this.props.boxVersion);
    }
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.editBoxVersion(
        this.props.boxTag,
        this.props.version,
        this.props.form.data
    );
  };

  onCancel = () => {
      this.props.router.push(
          `/boxes/${this.props.boxTag}/versions/${this.props.version}/`
      );
  };

  render() {
    return (
        <div>
          <PageHeader>Edit box version</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <BoxVersionForm
              pending={this.props.form.pending}
              submitTitle='Save'
              submitPendingTitle="Saving..."
              onSubmit={this.onSubmit}
              onCancel={this.onCancel}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName, version} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  const versionTag = `${boxTag} v${version}`;
  const boxVersion = state.entities.boxVersions[versionTag];
  return {
    myUsername: state.myUsername,
    form: state.forms.boxVersion,
    boxVersion,
    boxTag,
    username,
    boxName,
    version,
  }
}

export default connect(mapStateToProps, {
  fetchBoxVersion: actions.loadBoxVersion,
  editBoxVersion: actions.editBoxVersion,
  setFormData: actions.form.setData,
})(BoxVersionEditPage)
