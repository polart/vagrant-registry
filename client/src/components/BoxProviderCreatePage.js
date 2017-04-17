import React, {Component} from "react";
import {connect} from "react-redux";
import {Button, PageHeader} from "react-bootstrap";
import {merge} from "lodash";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MyBreadcrumbs from "./MyBreadcrumbs";
import BoxFileFormField from "./BoxFileFormField";


class BoxProviderCreatePage extends Component {
  state = {
    file: null,
  };

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

  render() {
    return (
        <div>
          <PageHeader>New box provider</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <form
              onSubmit={this.onSubmit}
          >
            <MyFormError model="boxProvider" />

            <MyFormField
                model='boxProvider.provider'
                type='text'
                label='Provider *'
            />

            <BoxFileFormField
                model='boxProvider.file'
                label='Box file'
                onChange={this.onFileInputChange}
            />

            <Button
                bsStyle="success"
                type="submit"
                disabled={this.props.form.pending}
            >
              Create
            </Button>
          </form>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName, version} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  return {
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
