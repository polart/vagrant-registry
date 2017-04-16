import React, {Component} from "react";
import {connect} from "react-redux";
import {Button, PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MyBreadcrumbs from "./MyBreadcrumbs";


class BoxVersionEditPage extends Component {
  componentDidMount() {
    this.props.setFormData('boxVersion', this.props.boxVersion);
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.editBoxVersion(
        this.props.boxTag,
        this.props.version,
        this.props.form.data
    );
  };

  render() {
    return (
        <div>
          <PageHeader>Edit box version</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <form
              onSubmit={this.onSubmit}
          >
            <MyFormError model="boxVersion" />

            <MyFormField
                model='boxVersion.version'
                type='text'
                label='Version *'
            />

            <MyFormField
                model='boxVersion.changes'
                type='textarea'
                label='Changes'
                rows='10'
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
  const {username, boxName, version} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  const versionTag = `${boxTag} v${version}`;
  const boxVersion = state.entities.boxVersions[versionTag];
  return {
    form: state.forms.boxVersion,
    boxVersion,
    boxTag,
    username,
    boxName,
    version,
  }
}

export default connect(mapStateToProps, {
  editBoxVersion: actions.editBoxVersion,
  setFormData: actions.form.setData,
})(BoxVersionEditPage)
