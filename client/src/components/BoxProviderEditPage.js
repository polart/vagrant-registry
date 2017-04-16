import React, {Component} from "react";
import {connect} from "react-redux";
import {Button, PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MyBreadcrumbs from "./MyBreadcrumbs";


class BoxProviderEditPage extends Component {
  componentDidMount() {
    this.props.setFormData('boxProvider', this.props.boxProvider);
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.editBoxProvider(
        this.props.boxTag,
        this.props.version,
        this.props.provider,
        this.props.form.data
    );
  };

  render() {
    return (
        <div>
          <PageHeader>Edit box provider</PageHeader>
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

            <Button
                bsStyle="success"
                type="submit"
                disabled={this.props.form.pending}
            >
              Save
            </Button>
          </form>
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
    form: state.forms.boxProvider,
    boxProvider,
    boxTag,
    username,
    boxName,
    version,
    provider,
  }
}

export default connect(mapStateToProps, {
  editBoxProvider: actions.editBoxProvider,
  setFormData: actions.form.setData,
})(BoxProviderEditPage)
