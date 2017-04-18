import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import {merge} from "lodash";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";
import BoxProviderForm from "./BoxProviderForm";


class BoxProviderCreatePage extends Component {
  state = {
    file: null,
  };

  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
    }
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBoxProvider(
        this.props.boxTag,
        this.props.version,
        merge({}, this.props.form.data, {file: this.state.file})
    );
  };

  onFileInputChange = (file) => {
    this.setState({ file });
  };

  onCancel = () => {
      this.props.router.push(
          `/boxes/${this.props.boxTag}/versions/${this.props.version}/`
      );
  };

  render() {
    return (
        <div>
          <PageHeader>New box provider</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <BoxProviderForm
              pending={this.props.form.pending}
              submitTitle='Create'
              submitPendingTitle="Creating..."
              onSubmit={this.onSubmit}
              onCancel={this.onCancel}
              onFileInputChange={this.onFileInputChange}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName, version} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  return {
    myUsername: state.myUsername,
    form: state.forms.boxProvider,
    boxTag,
    username,
    boxName,
    version,
  }
}

export default connect(mapStateToProps, {
  createBoxProvider: actions.createBoxProvider,
})(BoxProviderCreatePage)
