import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";
import BoxVersionForm from "./BoxVersionForm";


class BoxVersionCreatePage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
    }
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBoxVersion(this.props.boxTag, this.props.form.data);
  };

  onCancel = () => {
      this.props.router.push(
          `/boxes/${this.props.boxTag}/versions/`
      );
  };

  render() {
    return (
        <div>
          <PageHeader>New box version</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <BoxVersionForm
              pending={this.props.form.pending}
              submitTitle='Create'
              submitPendingTitle="Creating..."
              onSubmit={this.onSubmit}
              onCancel={this.onCancel}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName} = props.router.params;
  const boxTag = `${username}/${boxName}`;
  return {
    myUsername: state.myUsername,
    form: state.forms.boxVersion,
    boxTag,
    username,
    boxName,
  }
}

export default connect(mapStateToProps, {
  createBoxVersion: actions.createBoxVersion,
})(BoxVersionCreatePage)
