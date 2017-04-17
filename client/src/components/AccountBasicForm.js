import React, {Component} from "react";
import {connect} from "react-redux";
import {Button} from "react-bootstrap";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import {isEqual} from "lodash";


class AccountBasicForm extends Component {
  componentDidMount() {
    this.props.setFormData('account', this.props.user);
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.user, this.props.user)) {
      // For a case, when changing page or ordering.
      this.props.setFormData('account', this.props.user);
    }
  }

  componentWillUnmount() {
    this.props.setFormMessage('account', null);
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.updateAccount(this.props.user.username, this.props.form.data);
  };

  render() {
    return (
        <form
            onSubmit={this.onSubmit}
        >
          <MyFormError model="account" />

          <MyFormField
              model='account.username'
              type='text'
              label='Username *'
          />

          <Button
              bsStyle="success"
              type="submit"
              disabled={this.props.form.pending}
          >
            Edit
          </Button>
          {' '}
          {this.props.form.message && <span>{this.props.form.message}</span>}
        </form>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    form: state.forms.account,
  }
}

export default connect(mapStateToProps, {
  setFormData: actions.form.setData,
  setFormMessage: actions.form.setMessage,
  updateAccount: actions.updateAccount,
})(AccountBasicForm)
