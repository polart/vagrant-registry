import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader, Panel} from "react-bootstrap";
import * as actions from "../actions";
import BoxForm from "./BoxForm";
import MyBreadcrumbs from "./MyBreadcrumbs";


class BoxCreatePage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
    }
  }

  componentWillUnmount() {
    this.props.resetForm('box');
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBox(this.props.myUsername, this.props.form.data);
  };

  onCancel = () => {
    this.props.router.push('/');
  };

  render() {
    return (
        <div>
          <PageHeader>{this.props.myUsername}</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <Panel header="New box">
            <BoxForm
                pending={this.props.form.pending}
                submitTitle='Create'
                submitPendingTitle="Creating..."
                onSubmit={this.onSubmit}
                onCancel={this.onCancel}
            />
          </Panel>
        </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    myUsername: state.myUsername,
    form: state.forms.box,
  }
}

export default connect(mapStateToProps, {
  createBox: actions.createBox,
  resetForm: actions.form.reset,
})(BoxCreatePage)
