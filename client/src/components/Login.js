import React, {Component} from "react";
import {Link} from "react-router";
import {connect} from "react-redux";
import * as actions from "../actions";
import "../styles/login.css";
import MyFormError from "./MyFormError";
import MyFormField from "./MyFormField";
import MySubmitButton from "./MySubmitButton";


class Login extends Component {
  state = {
    formError: null,
  };

  onFormSubmit = (e) => {
    e.preventDefault();
    this.props.login(this.props.form.data);
  };

  render() {
    return (
        <div>
          <h1 className="text-center">Vagrant Registry</h1>

          <form onSubmit={this.onFormSubmit} className="login-form">
            <MyFormError model="login" />

            <MyFormField
                model='login.username'
                type='text'
                label='Username'
            />
            <MyFormField
                model='login.password'
                type='password'
                label='Password'
            />

            <MySubmitButton
                title='Sign In'
                pending={this.props.pending}
            />
            <Link className='login-view-boxes-link' to='/boxes/'>
              Or view public boxes
            </Link>
          </form>
        </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    form: state.forms.login,
  }
}

export default connect(mapStateToProps, {
  login: actions.login,
})(Login);
