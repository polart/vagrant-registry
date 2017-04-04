import React, { Component } from 'react';
import { FormGroup, FormControl, Button, Alert } from 'react-bootstrap';
import { Link } from 'react-router';
import { LocalForm, Control } from 'react-redux-form';
import { connect } from 'react-redux';

import * as auth from '../auth';
import * as actions from "../actions";
import '../styles/login.css';


class Login extends Component {
  state = {
    formError: null,
  };

  onFormSubmit = (values) => {
    auth.login(values.username, values.password, (loginData) => {
      if (loginData.authenticated) {
        this.props.setMyUsername(values.username);
        this.props.router.push(
            this.props.router.location.query.next || '/'
        );
      } else {
        const errors = loginData.data;
        if (errors.non_field_errors) {
          this.setState({formError: errors.non_field_errors.join(', ')});
        }
      }
    })
  };

  render() {
    return (
        <LocalForm
            onSubmit={this.onFormSubmit}
            className="login-form"
        >
          <h1 className="text-center">Vagrant Registry</h1>
          <h3>Please sign in</h3>

          {this.state.formError && <Alert bsStyle="danger">{this.state.formError}</Alert>}

          <FormGroup>
            <Control
                model=".username"
                type="text"
                placeholder="Username"
                component={FormControl}
                required
            />
          </FormGroup>
          <FormGroup>
            <Control
                model=".password"
                type="password"
                placeholder="Password"
                component={FormControl}
                required
            />
          </FormGroup>

          <Button type="submit" bsStyle="primary">
            Sign in
          </Button>

          <Link className='login-view-boxes-link' to='/boxes/'>
            Or view public boxes
          </Link>
        </LocalForm>
    );
  }
}

export default connect(null, {
  setMyUsername: actions.setMyUsername,
})(Login)
