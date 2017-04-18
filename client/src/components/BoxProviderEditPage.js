import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import {isEqual, merge} from "lodash";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";
import BoxProviderForm from "./BoxProviderForm";


class BoxProviderEditPage extends Component {
  state = {
    file: null,
  };

  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
      return;
    }
    if (!this.props.boxProvider) {
      this.props.loadBoxVersion(this.props.boxTag, this.props.version);
      return;
    }
    this.props.setFormData('boxProvider', this.props.boxProvider);
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.boxProvider, this.props.boxProvider)) {
      // For a case when box provider data loaded
      this.props.setFormData('boxProvider', this.props.boxProvider);
    }
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.editBoxProvider(
        this.props.boxTag,
        this.props.version,
        this.props.provider,
        merge({}, this.props.form.data, {file: this.state.file})
    );
  };

  onCancel = () => {
      this.props.router.push(
          `/boxes/${this.props.boxTag}/versions/${this.props.version}/`
      );
  };

  onFileInputChange = (file) => {
    this.setState({ file });
  };

  render() {
    return (
        <div>
          <PageHeader>Edit box provider</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <BoxProviderForm
              pending={this.props.form.pending}
              submitTitle='Save'
              submitPendingTitle="Saving..."
              onSubmit={this.onSubmit}
              onCancel={this.onCancel}
              onFileInputChange={this.onFileInputChange}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName, version, provider} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  const providerTag = `${boxTag} v${version} ${provider}`;
  const boxProvider = state.entities.boxProviders[providerTag];
  return {
    myUsername: state.myUsername,
    form: state.forms.boxProvider,
    boxProvider,
    boxTag,
    version,
    provider,
  }
}

export default connect(mapStateToProps, {
  loadBoxVersion: actions.loadBoxVersion,
  editBoxProvider: actions.editBoxProvider,
  setFormData: actions.form.setData,
})(BoxProviderEditPage)
