import React, {Component} from "react";
import {connect} from "react-redux";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MySubmitButton from "./MySubmitButton";


class AccountPasswordsForm extends Component {
  componentWillUnmount() {
    this.props.setFormMessage('changePassword', null);
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.changePassword(this.props.username, this.props.form.data);
  };

  render() {
    return (
        <form
            onSubmit={this.onSubmit}
        >
          <MyFormError model="changePassword" />

          <MyFormField
              model='changePassword.password'
              type='password'
              label='New password *'
          />

          <MyFormField
              model='changePassword.password2'
              type='password'
              label='Repeat password *'
          />

          <MySubmitButton
              title="Change"
              pendingTitle="Saving..."
              pending={this.props.form.pending}
          />
          {' '}
          {this.props.form.message && <span>{this.props.form.message}</span>}
        </form>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    form: state.forms.changePassword,
  }
}

export default connect(mapStateToProps, {
  setFormData: actions.form.setData,
  setFormMessage: actions.form.setMessage,
  changePassword: actions.changePassword
})(AccountPasswordsForm)
