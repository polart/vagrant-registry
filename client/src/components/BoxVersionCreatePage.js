import React, {Component} from "react";
import {connect} from "react-redux";
import {Button, PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MyBreadcrumbs from "./MyBreadcrumbs";


class BoxVersionCreatePage extends Component {
  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBoxVersion(this.props.boxTag, this.props.form.data);
  };

  render() {
    return (
        <div>
          <PageHeader>New box version</PageHeader>
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
              Create
            </Button>
          </form>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  return {
    form: state.forms.boxVersion,
    boxTag,
    username,
    boxName,
  }
}

export default connect(mapStateToProps, {
  createBoxVersion: actions.createBoxVersion,
})(BoxVersionCreatePage)
